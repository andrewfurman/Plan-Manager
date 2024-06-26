function deletePlan(planId) {
    fetch(`/delete_plan/${planId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            window.location.reload();
        } else {
            alert(data.error || 'An error occurred while deleting the plan');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete plan. Please try again later.');
    });
}

function updatePlan(planId) {
    fetch(`/update_plan/${planId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            window.location.reload();
        } else {
            alert(data.error || 'An error occurred while updating the plan');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update plan data. Please try again later.');
    });
}