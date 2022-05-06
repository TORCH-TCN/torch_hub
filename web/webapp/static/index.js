function deleteInstitution(institutionId) {
    fetch("/delete-institution", {
      method: "POST",
      body: JSON.stringify({ institutionId: institutionId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }