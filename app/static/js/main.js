// Alert handling
document.addEventListener("DOMContentLoaded", function () {
  // Close alert messages
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.remove();
      });
    }

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
      alert.remove();
    }, 5000);
  });

  // Form validation
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      const requiredFields = form.querySelectorAll("[required]");
      let isValid = true;

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          isValid = false;
          field.classList.add("error");
        } else {
          field.classList.remove("error");
        }
      });

      if (!isValid) {
        event.preventDefault();
      }
    });
  });

  // AJAX form submissions
  const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
  ajaxForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });

  const editForms = document.querySelectorAll(".edit-list-form");
  editForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });

  const deleteForms = document.querySelectorAll(".delete-list-form");
  deleteForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      if (!confirm("Are you sure you want to delete this list?")) {
        return;
      }

      fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
});

// Todo item interactions
function toggleExpand(itemId) {
  const item = document.querySelector(`[data-item-id="${itemId}"]`);
  const button = item.querySelector(".btn-expand");
  const icon = button.querySelector("i");
  const childrenContainer = item.querySelector(".children-container");

  fetch(`/item/${itemId}/expand`, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.expanded) {
        icon.classList.replace("fa-chevron-right", "fa-chevron-down");
        childrenContainer.style.display = "block";
      } else {
        icon.classList.replace("fa-chevron-down", "fa-chevron-right");
        childrenContainer.style.display = "none";
      }
    });
}

function toggleComplete(itemId) {
  fetch(`/item/${itemId}/toggle`, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const item = document.querySelector(`[data-item-id="${itemId}"]`);
      const title = item.querySelector(".item-title");
      const button = item.querySelector(".btn-toggle i");

      if (data.completed) {
        title.classList.add("completed");
        button.classList.replace("fa-circle", "fa-check-circle");
      } else {
        title.classList.remove("completed");
        button.classList.replace("fa-check-circle", "fa-circle");
      }
    });
}

// Modal handling
function showMoveModal(itemId) {
  const modal = document.getElementById("moveModal");
  const form = document.getElementById("moveItemForm");
  form.action = `/item/${itemId}/move`;
  modal.style.display = "block";
}

function closeMoveModal() {
  const modal = document.getElementById("moveModal");
  modal.style.display = "none";
}

// Close modal when clicking outside
window.onclick = function (event) {
  const modal = document.getElementById("moveModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

function showEditForm(listId) {
  document.getElementById(`edit-form-${listId}`).style.display = 'flex';
}

function closeEditForm(listId) {
  document.getElementById(`edit-form-${listId}`).style.display = 'none';
}
