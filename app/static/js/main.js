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
        storeScrollPosition();

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
                // Get the containing list element
                const list = this.closest('.todo-list');

                if (this.classList.contains('create-list-form')) {
                    // Refresh the entire lists container
                    updateListsContainer();
                }
                else if (this.classList.contains('toggle-completed-form')) {
                    // Handle toggle completed view
                    const button = this.querySelector('button');
                    const icon = button.querySelector('i');
                    if (data.show_completed) {
                        icon.classList.replace('fa-eye', 'fa-eye-slash');
                        button.title = 'Hide completed tasks';
                    } else {
                        icon.classList.replace('fa-eye-slash', 'fa-eye');
                        button.title = 'Show completed tasks';
                    }
                    // Update just this list's items
                    if (list) {
                        const listId = list.dataset.listId;
                        updateListItems(listId);
                    }
                }
                else if (list) {
                    // For other operations, just update the affected list
                    const listId = list.dataset.listId;
                    updateListItems(listId);
                }

                // Clear any input fields
                const inputs = this.querySelectorAll('input[type="text"]');
                inputs.forEach(input => input.value = '');

                // Hide any forms that might be open
                const editForms = document.querySelectorAll('.edit-list-form, .edit-item-form, .subitem-form');
                editForms.forEach(form => form.style.display = 'none');

                restoreScrollPosition();
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

  // Restore scroll position if it exists
  const scrollPosition = localStorage.getItem('scrollPosition');
  if (scrollPosition) {
      window.scrollTo(0, parseInt(scrollPosition));
      localStorage.removeItem('scrollPosition');
  }

  // Store scroll position before any form submission
  document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function() {
          localStorage.setItem('scrollPosition', window.scrollY);
      });
  });

  // Store scroll position before any AJAX request that might reload content
  const storeScrollPosition = () => {
      localStorage.setItem('scrollPosition', window.scrollY);
  };

  // Add scroll position storage to existing AJAX handlers
  document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
      form.addEventListener('submit', storeScrollPosition);
  });

  // Also store position before any clicks that might trigger page updates
  document.querySelectorAll('.btn-toggle, .btn-expand, .btn-edit, .btn-delete').forEach(btn => {
      btn.addEventListener('click', storeScrollPosition);
  });
});

// Generic AJAX form submission handler
function handleAjaxSubmission(form) {
    storeScrollPosition();
    return fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const list = form.closest('.todo-list');

            if (form.classList.contains('create-list-form')) {
                updateListsContainer();
            }
            else if (form.classList.contains('toggle-completed-form')) {
                const button = form.querySelector('button');
                const icon = button.querySelector('i');
                if (data.show_completed) {
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                    button.title = 'Hide completed tasks';
                } else {
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                    button.title = 'Show completed tasks';
                }
                if (list) {
                    updateListItems(list.dataset.listId);
                }
            }
            else if (list) {
                updateListItems(list.dataset.listId);
            } else {
                updateListsContainer();
            }

            // Clear form inputs
            const inputs = form.querySelectorAll('input[type="text"]');
            inputs.forEach(input => input.value = '');

            // Hide any open forms
            const editForms = document.querySelectorAll('.edit-list-form, .edit-item-form, .subitem-form');
            editForms.forEach(form => form.style.display = 'none');
        }
        restoreScrollPosition();
    })
    .catch(error => console.error('Error:', error));
}

// Replace all form submit handlers with the new one
document.addEventListener("DOMContentLoaded", function() {
    // ...existing DOMContentLoaded code...

    // Handle all AJAX forms
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleAjaxSubmission(this);
        });
    });

    // Replace existing handlers with new ones
    document.querySelectorAll(".edit-list-form, .edit-item-form, .delete-list-form, .delete-item-form").forEach(form => {
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            if (form.classList.contains('delete-list-form') || form.classList.contains('delete-item-form')) {
                if (!confirm("Are you sure you want to delete this item?")) {
                    return;
                }
            }
            handleAjaxSubmission(this);
        });
    });

    // Replace toggle handlers
    document.querySelectorAll('.toggle-completed-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleAjaxSubmission(this);
        });
    });
});

// Update toggleExpand to use AJAX
function toggleExpand(itemId) {
    storeScrollPosition();
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
        restoreScrollPosition();
    });
}

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

// Function to update the entire lists container
function updateListsContainer() {
    storeScrollPosition();
    fetch('/todos/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newListsContainer = doc.querySelector('.lists-container');
        const currentListsContainer = document.querySelector('.lists-container');
        if (newListsContainer && currentListsContainer) {
            currentListsContainer.innerHTML = newListsContainer.innerHTML;
        }
    })
    .then(() => {
        restoreScrollPosition();
    });
}

// Function to update a single list's items
function updateListItems(listId) {
    storeScrollPosition();
    fetch(`/list/${listId}/items`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        const itemsContainer = document.querySelector(`.todo-list[data-list-id="${listId}"] .items-container`);
        if (itemsContainer) {
            itemsContainer.innerHTML = html;
        }
    })
    .then(() => {
        restoreScrollPosition();
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

// Helper functions for scroll position
function storeScrollPosition() {
    localStorage.setItem('scrollPosition', window.scrollY);
}

function restoreScrollPosition() {
    const scrollPosition = localStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        localStorage.removeItem('scrollPosition');
    }
}

// Replace all window.location.reload() calls with AJAX updates
document.querySelectorAll(".edit-list-form, .edit-item-form, .delete-list-form, .delete-item-form").forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        storeScrollPosition();

        if (this.classList.contains('delete-list-form') || this.classList.contains('delete-item-form')) {
            if (!confirm('Are you sure you want to delete this?')) {
                return;
            }
        }

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
                const list = this.closest('.todo-list');
                if (list) {
                    const listId = list.dataset.listId;
                    if (this.classList.contains('delete-list-form')) {
                        updateListsContainer();
                    } else {
                        updateListItems(listId);
                    }
                }
                // Clear any forms that might be open
                document.querySelectorAll('.edit-list-form, .edit-item-form').forEach(f => {
                    f.style.display = 'none';
                });
            }
            restoreScrollPosition();
        });
    });
});

// Update toggleExpand to avoid page reload
function toggleExpand(itemId) {
    storeScrollPosition();
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
            if (childrenContainer) {
                childrenContainer.style.display = 'block';
            }
        } else {
            icon.classList.replace('fa-chevron-down', 'fa-chevron-right');
            if (childrenContainer) {
                childrenContainer.style.display = 'none';
            }
        }
        restoreScrollPosition();
    });
}
