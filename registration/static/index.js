function markTouched(e) {
  var classes = e.target.className || '';
  if (classes.indexOf('touched') === -1) {
    e.target.className += ' touched';
  }
}

var inputs = document.querySelectorAll('input, select, textarea')
for (var i = 0; i < inputs.length; i++) {
  inputs[i].addEventListener('click', markTouched);
  inputs[i].addEventListener('focus', markTouched);
  inputs[i].addEventListener('blur', markTouched);
}


// function setColor(e) {
//   var t = e.target;
//   console.log(t.value)
//   if (t.value.length == 0){
//     t.style.color = "#204F80"
//   }else{
//     t.style.color = "white"
//   }

//   if (t.name == "needs_reimbursement"){
//     if (t.value == 'Yes'){
//       travelMethod.style.display = "block";
//     } else {
//       travelMethod.style.display = "none"
//     }
//   }
// }

// var selects = document.querySelectorAll('select');
// var travelMethod = document.querySelector('label[title="preferred_travel_method"]')
// for (var i=0; i< selects.length; i++) {
//   selects[i].addEventListener('change', setColor);
// }

function ensureChecked(e){
  var checks = document.querySelectorAll('input[type="checkbox"][required]:not(:checked)')
  
  if (checks.length > 0){
    e.preventDefault();
    console.log(checks)
    checks.forEach(function(check){
      if (check.className.indexOf('invalid') == -1){
        check.className += ' invalid' 
      }
    })
  }
}

document.querySelector('form').addEventListener('submit', ensureChecked)