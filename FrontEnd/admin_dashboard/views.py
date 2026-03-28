'''
Author: Fenix Do
Date: 03/28/2026
Purpose: Coordinates backend Django processing, returning proper HTML templates or JSON endpoints.
'''
import json
import os
import sqlite3
import subprocess
import sys
import threading
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

# ── paths ──────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEASUREMENTS_DB = os.path.join(REPO_ROOT, 'Measurements.db')
LOG_FILE = os.path.join(REPO_ROOT, 'BackEnd', 'log.txt')
COMMANDS_SCRIPT = os.path.join(REPO_ROOT, 'BackEnd', 'commands.py')


def _write_log(message: str) -> None:
    """Append a timestamped log entry to LOG_FILE."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {message}\n'
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception:
        pass  # don't let logging failures break the app


# ── in-memory script output buffer ────────────────────────────────────
_script_output_lock = threading.Lock()
_script_output_lines: list[str] = []
_script_running = False
_last_exit_code = None

DATA_MODERATOR_GROUP = 'Data Moderator'


def _get_user_role(user):
    """Return 'admin', 'data_moderator', or None."""
    if user.is_staff:
        return 'admin'
    if user.groups.filter(name=DATA_MODERATOR_GROUP).exists():
        return 'data_moderator'
    return None


def _has_dashboard_access(user):
    """Admins and Data Moderators can access the dashboard."""
    return user.is_active and _get_user_role(user) is not None


def _dashboard_required(view_fn):
    """Decorator: require admin or data-moderator role."""
    decorated = login_required(
        user_passes_test(_has_dashboard_access, login_url='/admin/login/')(view_fn),
        login_url='/admin/login/',
    )
    return decorated


def _admin_only(view_fn):
    """Decorator: require admin (is_staff) role."""
    decorated = login_required(
        user_passes_test(lambda u: u.is_active and u.is_staff, login_url='/admin/login/')(view_fn),
        login_url='/admin/login/',
    )
    return decorated


# ══════════════════════════════════════════════════════════════════════
#  Page views
# ══════════════════════════════════════════════════════════════════════

def admin_login(request):
    """Render login form and authenticate."""
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and _has_dashboard_access(user):
            login(request, user)
            next_url = request.GET.get('next', '/admin/')
            return redirect(next_url)
        else:
            error = 'Invalid credentials or insufficient permissions.'
    return render(request, 'admin_dashboard/login.html', {'error': error})


def admin_logout(request):
    logout(request)
    return redirect('/admin/login/')


@_dashboard_required
def admin_dashboard(request):
    role = _get_user_role(request.user)
    return render(request, 'admin_dashboard/dashboard.html', {
        'current_user': request.user,
        'user_role': role,  # 'admin' or 'data_moderator'
    })


# ══════════════════════════════════════════════════════════════════════
#  Console Log APIs
# ══════════════════════════════════════════════════════════════════════

def _get_command_catalog():
    """Best-effort command metadata from BackEnd.commands."""
    try:
        from BackEnd.commands import get_command_catalog
        commands = get_command_catalog()
    except Exception:
        commands = []

    if not commands:
        commands = [
            {
                'id': 'listAllSources',
                'label': 'List All Sources',
                'description': 'List all source files in the BackEnd/SourceFiles folder.',
            },
            {
                'id': 'listStations',
                'label': 'List Stations',
                'description': 'List all stations for a specified source.',
            }
        ]

    return commands


@_dashboard_required
@require_GET
def api_commands(request):
    """Return available backend commands for dashboard UI."""
    commands = _get_command_catalog()
    return JsonResponse({
        'commands': commands,
        'default': commands[0]['id'] if commands else 'listAllSources',
    })

@_dashboard_required
@require_GET
def api_logs(request):
    """Return the last N lines from the log file + any script output."""
    max_lines = int(request.GET.get('lines', 200))
    log_lines = []

    # Read from log file
    if os.path.isfile(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                log_lines = f.readlines()[-max_lines:]
        except Exception:
            log_lines = ['[Error reading log file]']

    # Append in-memory script output
    with _script_output_lock:
        script_lines = list(_script_output_lines)

    combined = [l.rstrip('\n\r') for l in log_lines] + script_lines

    return JsonResponse({
        'lines': combined[-max_lines:],
        'running': _script_running,
        'exit_code': _last_exit_code,
    })



@_admin_only
@require_POST
def api_run_script(request):
    """Run selected backend command in background and capture output."""
    global _script_running, _last_exit_code

    if _script_running:
        return JsonResponse({'status': 'already_running'})

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        body = {}

    commands = _get_command_catalog()
    command_ids = {c.get('id') for c in commands}
    command_id = body.get('command') or (commands[0]['id'] if commands else 'listAllSources')
    if command_id not in command_ids:
        return JsonResponse({'error': f'Unknown command: {command_id}'}, status=400)

    selected = next((c for c in commands if c.get('id') == command_id), {'label': command_id})
    selected_label = selected.get('label', command_id)

    def _run():
        global _script_running, _last_exit_code
        _script_running = True
        _last_exit_code = None
        _write_log(f'SCRIPT RUN by {request.user.username}: {selected_label} started')
        with _script_output_lock:
            _script_output_lines.clear()
            _script_output_lines.append(f'─── Starting {selected_label} ({command_id}) ───')

        try:
            py_code = f"import sys; sys.path.insert(0, r'{REPO_ROOT}'); import BackEnd.commands as cmds; res = getattr(cmds, '{command_id}')(); print('Returned:', res) if res is not None else None"
            proc = subprocess.Popen(
                [sys.executable, '-c', py_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=REPO_ROOT,
            )
            for line in proc.stdout:
                with _script_output_lock:
                    _script_output_lines.append(line.rstrip('\n\r'))
            proc.wait()
            _last_exit_code = proc.returncode
            with _script_output_lock:
                _script_output_lines.append(
                    f'─── {selected_label} finished (exit code {proc.returncode}) ───'
                )
        except Exception as exc:
            with _script_output_lock:
                _script_output_lines.append(f'[ERROR] {exc}')
            _last_exit_code = 1
        finally:
            _script_running = False

    threading.Thread(target=_run, daemon=True).start()
    return JsonResponse({'status': 'started', 'command': command_id, 'label': selected_label})


# ══════════════════════════════════════════════════════════════════════
#  Data Insertion APIs
# ══════════════════════════════════════════════════════════════════════

@_dashboard_required
@require_GET
def api_tables(request):
    """List all tables in Measurements.db (excluding internal tables)."""
    try:
        conn = sqlite3.connect(MEASUREMENTS_DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = [r[0] for r in cur.fetchall() if r[0] and not r[0].startswith('temp_')]
        conn.close()
        return JsonResponse({'tables': tables})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@_dashboard_required
@require_GET
def api_table_columns(request, table_name):
    """Return column info for a given table."""
    try:
        conn = sqlite3.connect(MEASUREMENTS_DB)
        cur = conn.cursor()
        cur.execute(f'PRAGMA table_info("{table_name}")')
        columns = [
            {'name': r[1], 'type': r[2], 'notnull': bool(r[3]), 'pk': bool(r[5])}
            for r in cur.fetchall()
        ]
        conn.close()
        return JsonResponse({'table': table_name, 'columns': columns})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@_dashboard_required
@require_POST
def api_insert(request):
    """Insert a row into a Measurements.db table."""
    try:
        body = json.loads(request.body)
        table_name = body.get('table', '')
        row_data = body.get('data', {})

        if not table_name or not row_data:
            return JsonResponse({'error': 'table and data are required'}, status=400)

        # Validate table exists
        conn = sqlite3.connect(MEASUREMENTS_DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cur.fetchone():
            conn.close()
            return JsonResponse({'error': f'Table "{table_name}" not found'}, status=404)

        # Get valid columns
        cur.execute(f'PRAGMA table_info("{table_name}")')
        valid_cols = {r[1] for r in cur.fetchall()}

        # Filter to valid columns only
        filtered = {k: v for k, v in row_data.items() if k in valid_cols and v != ''}
        if not filtered:
            conn.close()
            return JsonResponse({'error': 'No valid column data provided'}, status=400)

        cols = list(filtered.keys())
        placeholders = ', '.join(['?'] * len(cols))
        col_names = ', '.join([f'"{c}"' for c in cols])
        values = list(filtered.values())

        cur.execute(f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})', values)
        conn.commit()
        conn.close()

        username = request.user.username if request.user.is_authenticated else 'unknown'
        _write_log(f'DATA INSERT by {username}: table="{table_name}", data={filtered}')

        return JsonResponse({'status': 'ok', 'inserted': filtered})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        username = request.user.username if request.user.is_authenticated else 'unknown'
        _write_log(f'DATA INSERT ERROR by {username}: table="{table_name}", error={e}')
        return JsonResponse({'error': str(e)}, status=500)


# ══════════════════════════════════════════════════════════════════════
#  User Management APIs
# ══════════════════════════════════════════════════════════════════════

@_admin_only
@require_http_methods(['GET', 'POST'])
def api_users_list(request):
    """GET: list users.  POST: create a new user."""
    # Ensure Data Moderator group exists
    Group.objects.get_or_create(name=DATA_MODERATOR_GROUP)

    if request.method == 'GET':
        users_qs = User.objects.all().order_by('username')
        users = []
        for u in users_qs:
            role = 'admin' if u.is_staff else (
                'data_moderator' if u.groups.filter(name=DATA_MODERATOR_GROUP).exists() else 'user'
            )
            users.append({
                'id': u.id,
                'username': u.username,
                'email': u.email or '',
                'role': role,
                'is_active': u.is_active,
                'date_joined': u.date_joined.isoformat(),
            })
        return JsonResponse({'users': users})

    # POST — create user
    try:
        body = json.loads(request.body)
        username = body.get('username', '').strip()
        password = body.get('password', '')
        email = body.get('email', '').strip()
        role = body.get('role', 'data_moderator')  # 'admin' or 'data_moderator'

        if not username or not password:
            return JsonResponse({'error': 'username and password are required'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=(role == 'admin'),
        )
        if role == 'data_moderator':
            group, _ = Group.objects.get_or_create(name=DATA_MODERATOR_GROUP)
            user.groups.add(group)

        return JsonResponse({
            'status': 'created',
            'user': _serialize_user(user),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _serialize_user(user):
    role = _get_user_role(user) or 'user'
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email or '',
        'role': role,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
    }


@_admin_only
@require_http_methods(['PUT', 'DELETE'])
def api_user_detail(request, user_id):
    """PUT: update user.  DELETE: remove user."""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if request.method == 'DELETE':
        if user.pk == request.user.pk:
            return JsonResponse({'error': 'Cannot delete yourself'}, status=400)
        user.delete()
        return JsonResponse({'status': 'deleted'})

    # PUT — update
    try:
        body = json.loads(request.body)
        if 'email' in body:
            user.email = body['email']
        if 'role' in body:
            new_role = body['role']
            if user.pk == request.user.pk:
                return JsonResponse({'error': 'Cannot change your own role'}, status=400)
            # Update is_staff and group membership
            dm_group, _ = Group.objects.get_or_create(name=DATA_MODERATOR_GROUP)
            if new_role == 'admin':
                user.is_staff = True
                user.groups.remove(dm_group)
            elif new_role == 'data_moderator':
                user.is_staff = False
                user.groups.add(dm_group)
            else:
                user.is_staff = False
                user.groups.remove(dm_group)
        if 'is_active' in body:
            if user.pk == request.user.pk:
                return JsonResponse({'error': 'Cannot deactivate yourself'}, status=400)
            user.is_active = body['is_active']
        if 'password' in body and body['password']:
            user.set_password(body['password'])
        user.save()
        return JsonResponse({
            'status': 'updated',
            'user': _serialize_user(user),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
