const form = document.getElementById('register-form');
const submitButton = document.getElementById('register-btn');
const requiredFields = form.querySelectorAll('input[required], select[required]');

function checkFormCompletion() {
    let allFieldsFilled = true;

    // Check if all required fields are filled
    requiredFields.forEach((field) => {
        if (!field.value.trim()) {
            allFieldsFilled = false;
        }
    });

    // Enable or disable the submit button based on form completion
    if (allFieldsFilled) {
        submitButton.disabled = false;
        submitButton.classList.remove('bg-gray-300', 'cursor-not-allowed');
        submitButton.classList.add('bg-red-400', 'hover:bg-red-500');
    } else {
        submitButton.disabled = true;
        submitButton.classList.remove('bg-red-400', 'hover:bg-red-500');
        submitButton.classList.add('bg-gray-300', 'cursor-not-allowed');
    }
}

// Attach event listeners to all required fields
requiredFields.forEach((field) => {
    field.addEventListener('input', checkFormCompletion);
});