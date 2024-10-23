document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('register-form');
    const inputs = form.querySelectorAll('input, select');
    const submitButton = form.querySelector('button[type="submit"]');

    function checkFormCompletion() {
        let isFormComplete = true;

        // Loop through all inputs and check if any are empty
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isFormComplete = false;
            }
        });

        // Enable or disable the submit button based on form completion
        if (isFormComplete) {
            submitButton.disabled = false;
            submitButton.classList.remove('bg-gray-300', 'cursor-not-allowed');
            submitButton.classList.add('bg-red-500', 'cursor-pointer');
        } else {
            submitButton.disabled = true;
            submitButton.classList.remove('bg-red-500', 'cursor-pointer');
            submitButton.classList.add('bg-gray-300', 'cursor-not-allowed');
        }
    }

    // Add event listeners to all form inputs to track changes
    inputs.forEach(input => {
        input.addEventListener('input', checkFormCompletion);
    });
});
