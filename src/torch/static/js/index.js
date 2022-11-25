Dropzone.options.dropbox = {
  uploadMultiple: true,
  parallelUploads: 1,
  paramName: (n) => 'file',
  init: function() {
    this.on("addedfile", file => {
      console.log("A file has been added");
      let element = document.getElementById("fileName");
      if (element) {
        element.innerHTML = file.name;
        document.getElementById("uploadingMessageContainer").style.display="";
      }
      const incrementCounter = new CustomEvent('increment-counter');
      window.dispatchEvent(incrementCounter);
    });
    this.on("complete", file => {
      console.log('uploaded');
      //this.removeFile(file);
      const decrementCounter = new CustomEvent('decrement-counter');
      window.dispatchEvent(decrementCounter);
    });
    this.on("successmultiple", () => {
      console.log('successmultiple');
      // var closeModal = new CustomEvent('close-modal');
      // window.dispatchEvent(closeModal);
    });
  }
};
function deleteInstitution(institutionId) {
  if (confirm("Are you sure you want to remove this institution?") === true) {
    fetch("/delete-institution", {
      method: "POST",
      body: JSON.stringify({ institutionId: institutionId }),
    }).then((_res) => {
      window.location.href = "/institutions";
    });
  }
}

let selectedUserId = 0;

function openRoleModal(userId){
  console.log('openRoleModal',userId);
  selectedUserId = userId;
  $("#exampleModal").modal()
}

function changeUserActive(userId, active){

  let str = eval(active.toLowerCase()) === true ? "deactivate" : "activate";

  if (confirm(`Are you sure you want to ${str} this user?`) === true) {
    fetch("/users/" + userId + "/active", {
      method: "POST",
      body: JSON.stringify({ userId: userId }),
    }).then((_res) => {
      window.location.href = "/users";
    });
  } 
}

function addRoleToUser(){

  const selectedRole = document.getElementById('selectedRole').value;
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
  
  if (confirm("Are you sure you want to remove this role?") === true) {
    fetch("/users/" + userId + "/roles", {
      method: "DELETE",
      body: JSON.stringify({ userId: userId, role: role }),
    }).then((_res) => {
      window.location.href = "/users";
    });
  } 

}

function deleteWorkflowSetting(workflowSettingId) {
  if (confirm("Are you sure you want to remove this workflow setting?") === true) {
    fetch("/workflows/settings/" + workflowSettingId, {
      method: "DELETE",
      body: JSON.stringify({ workflowSettingId: workflowSettingId }),
    }).then((_res) => {
      window.location.href = "/workflows/settings";
    });
  }
}
