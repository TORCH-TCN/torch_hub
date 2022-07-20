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

function changeUserActive(userId, active){
    
  str = eval(active.toLowerCase()) == true ? "deactivate" : "activate";

  if (confirm(`Are you sure you want to ${str} this user?`) == true) {
    fetch("/users/" + userId + "/active", {
      method: "POST",
      body: JSON.stringify({ userId: userId }),
    }).then((_res) => {
      window.location.href = "/users";
    });
  } 
}

function addRoleToUser(){
 
  var selectedRole = document.getElementById('selectedRole').value;
  console.log('addRoleToUser', selectedUserId, selectedRole);

  fetch("/users/"+selectedUserId+"/roles", {
    method: "POST",
    body: JSON.stringify({ userId: selectedUserId, role: selectedRole }),
  }).then((_res) => {
    $("#exampleModal").modal('hide')
    window.location.href = "/users";
  });
}

function deleteRoleFromUser(userId, role){
  
  if (confirm("Are you sure you want to remove this role?") == true) {
    fetch("/users/" + userId + "/roles", {
      method: "DELETE",
      body: JSON.stringify({ userId: userId, role: role }),
    }).then((_res) => {
      window.location.href = "/users";
    });
  } 

}