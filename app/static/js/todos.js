// ...existing code...

// Function to open move item modal
function openMoveItemModal(itemId) {
    document.getElementById('move-item-id').value = itemId;
    const modal = document.getElementById('move-item-modal');
    const instance = M.Modal.getInstance(modal);
    instance.open();
}

// ...existing code...
