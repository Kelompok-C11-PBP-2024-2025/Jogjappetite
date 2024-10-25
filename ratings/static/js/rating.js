document.addEventListener("DOMContentLoaded", function () {
    const addRatingBtn = document.getElementById("add-rating-btn");
    const ratingModal = document.getElementById("rating-modal");
    const modalBody = document.getElementById("modal-body");
    const closeModal = document.querySelector(".close-modal");

    // Open the modal when "Add Rating" button is clicked
    addRatingBtn.addEventListener("click", function () {
        fetch(`/ratings/restaurants/{{ restaurant.id }}/add-rating/`)
            .then(response => response.text())
            .then(data => {
                modalBody.innerHTML = data;
                ratingModal.style.display = "block";
            });
    });

    // Close the modal when the "x" button is clicked
    closeModal.addEventListener("click", function () {
        ratingModal.style.display = "none";
    });

    // Handle form submission with AJAX
    document.body.addEventListener("submit", function (event) {
        if (event.target.id === "rating-form") {
            event.preventDefault();

            const formData = new FormData(event.target);
            fetch(event.target.action, {
                method: "POST",
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Rating added successfully!");
                        ratingModal.style.display = "none";
                        window.location.reload();  // Reload the page to show the new rating
                    } else {
                        alert("Error: " + JSON.stringify(data.errors));
                    }
                });
        }
    });

    // Handle delete and edit actions (assume there are buttons with class "edit-rating" and "delete-rating")
    document.body.addEventListener("click", function (event) {
        if (event.target.classList.contains("delete-rating")) {
            const ratingId = event.target.getAttribute("data-id");
            fetch(`/ratings/${ratingId}/delete/`, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Rating deleted successfully!");
                        window.location.reload();
                    }
                });
        }

        if (event.target.classList.contains("edit-rating")) {
            const ratingId = event.target.getAttribute("data-id");
            fetch(`/ratings/${ratingId}/edit/`)
                .then(response => response.text())
                .then(data => {
                    modalBody.innerHTML = data;
                    ratingModal.style.display = "block";
                });
        }
    });
});
