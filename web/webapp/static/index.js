function deleteInstitution(institutionId) {
    fetch("/delete-institution", {
      method: "POST",
      body: JSON.stringify({ institutionId: institutionId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

var selectedUserId = 0;

function openRoleModal(userId){
  console.log('openRoleModal',userId);
  selectedUserId = userId;
  $("#exampleModal").modal()
}

function addRoleToUser(){
 
  var selectedRole = document.getElementById('selectedRole').value;
  console.log('addRoleToUser', selectedUserId, selectedRole);

  fetch("/assign-role", {
    method: "POST",
    body: JSON.stringify({ userId: selectedUserId, role: selectedRole }),
  }).then((_res) => {
    $("#exampleModal").modal('hide')
    window.location.href = "/users";
  });
}

function deleteRoleFromUser(userId, role){
  
  if (confirm("Are you sure you want to remove this role?") == true) {
    fetch("/delete-role-user", {
      method: "POST",
      body: JSON.stringify({ userId: userId, role: role }),
    }).then((_res) => {
      window.location.href = "/users";
    });
  } 

}