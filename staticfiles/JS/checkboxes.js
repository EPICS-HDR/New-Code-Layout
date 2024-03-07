function limitLocations() {
    var checkboxes = document.getElementsByName("location");
    var checkedCount = 0;
    
    for (var i = 0; i < checkboxes.length; i++) {
      if (checkboxes[i].checked) {
        checkedCount++;
      }
    }
    
    if (checkedCount >= 3) {
      for (var i = 0; i < checkboxes.length; i++) {
        if (!checkboxes[i].checked) {
          checkboxes[i].disabled = true;
        }
      }
    } else {
      for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].disabled = false;
      }
    }
  }