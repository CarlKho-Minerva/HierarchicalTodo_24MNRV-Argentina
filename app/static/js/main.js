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

  // Handle all AJAX form submissions
  document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        fetch(this.action, {
            method: this.method,
            body: new FormData(this),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (this.classList.contains('toggle-completed-form')) {
                    // Update the eye icon
                    const button = this.querySelector('button');
                    const icon = button.querySelector('i');
                    if (data.show_completed) {
                        icon.classList.replace('fa-eye', 'fa-eye-slash');
                        button.title = 'Hide completed tasks';
                    } else {
                        icon.classList.replace('fa-eye-slash', 'fa-eye');
                        button.title = 'Show completed tasks';
                    }

                    // Update the items container without page reload
                    const listId = this.closest('.todo-list').dataset.listId;
                    fetch(`/list/${listId}/items`, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.text())
                    .then(html => {
                        const itemsContainer = this.closest('.todo-list').querySelector('.items-container');
                        itemsContainer.innerHTML = html;
                    });
                } else {
                    // Handle other form submissions as before
                    window.location.reload();
                }
            }
        })
        .catch(error => console.error('Error:', error));
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

  const editItemForms = document.querySelectorAll(".edit-item-form");
  editItemForms.forEach((form) => {
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

  const deleteItemForms = document.querySelectorAll(".delete-item-form");
  deleteItemForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      if (!confirm("Are you sure you want to delete this item?")) {
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

  document.querySelectorAll('.toggle-completed-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        fetch(this.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const button = this.querySelector('button');
                const icon = button.querySelector('i');
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
                button.title = data.show_completed ? 'Hide completed tasks' : 'Show completed tasks';
                location.reload(); // Refresh to update the list view
            }
        });
    });
  });
});

function handleToggleResponse(form, data) {
  const itemContainer = form.closest('.todo-item');
  const toggleButton = form.querySelector('.btn-toggle');
  const itemTitle = itemContainer.querySelector('.item-title');
  const icon = toggleButton.querySelector('i');

  if (data.completed) {
      toggleButton.classList.add('completed');
      itemTitle.classList.add('completed');
      icon.classList.replace('fa-circle-dot', 'fa-check-circle');
  } else {
      toggleButton.classList.remove('completed');
      itemTitle.classList.remove('completed');
      icon.classList.replace('fa-check-circle', 'fa-circle-dot');
  }
}

function handleCompletedViewResponse(form, data) {
  const button = form.querySelector('button');
  const icon = button.querySelector('i');

  if (data.show_completed) {
      icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
      icon.classList.replace('fa-eye-slash', 'fa-eye');
  }

  // Reload just the items container
  const listId = form.closest('.todo-list').dataset.listId;
  reloadItemsContainer(listId);
}

function reloadItemsContainer(listId) {
  fetch(`/list/${listId}/items`, {
      headers: {
          'X-Requested-With': 'XMLHttpRequest'
      }
  })
  .then(response => response.text())
  .then(html => {
      const list = document.querySelector(`.todo-list[data-list-id="${listId}"]`);
      const itemsContainer = list.querySelector('.items-container');
      itemsContainer.innerHTML = html;
  });
}

// Todo item interactions
function toggleExpand(itemId) {
  fetch(`/item/${itemId}/expand`, {
    method: 'POST',
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => response.json())
  .then(data => {
      const item = document.querySelector(`[data-item-id="${itemId}"]`);
      const button = item.querySelector('.btn-expand');
      const icon = button.querySelector('i');
      const childrenContainer = item.querySelector('.children-container');

      if (data.expanded) {
          icon.classList.replace('fa-chevron-right', 'fa-chevron-down');
          childrenContainer.style.display = 'block';
      } else {
          icon.classList.replace('fa-chevron-down', 'fa-chevron-right');
          childrenContainer.style.display = 'none';
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

function showEditItemForm(itemId) {
  document.getElementById(`edit-item-form-${itemId}`).style.display = 'flex';
}

function closeEditItemForm(itemId) {
  document.getElementById(`edit-item-form-${itemId}`).style.display = 'none';
}
