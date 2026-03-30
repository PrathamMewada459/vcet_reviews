// ===== VCET Review System — main.js =====

// Star picker logic
var selectedRating = 0;

var starPicker = document.getElementById("starPicker");
if (starPicker) {
    var stars = starPicker.querySelectorAll(".star");

    stars.forEach(function(star) {
        // Hover effect
        star.addEventListener("mouseover", function() {
            var val = parseInt(this.getAttribute("data-val"));
            highlightStars(val);
        });
        star.addEventListener("mouseout", function() {
            highlightStars(selectedRating);
        });
        // Click to select
        star.addEventListener("click", function() {
            selectedRating = parseInt(this.getAttribute("data-val"));
            document.getElementById("rating").value = selectedRating;
            highlightStars(selectedRating);
        });
    });
}

function highlightStars(upTo) {
    var stars = document.querySelectorAll("#starPicker .star");
    stars.forEach(function(s) {
        var val = parseInt(s.getAttribute("data-val"));
        if (val <= upTo) {
            s.classList.add("active");
        } else {
            s.classList.remove("active");
        }
    });
}

// Character count for textarea
var reviewTextarea = document.getElementById("review-text");
var charCount = document.getElementById("char-count");
if (reviewTextarea && charCount) {
    reviewTextarea.addEventListener("input", function() {
        var len = this.value.length;
        charCount.textContent = len + " / 500";
        if (len > 450) {
            charCount.style.color = "#e74c3c";
        } else {
            charCount.style.color = "";
        }
    });
}

// Submit review via fetch (no page reload)
function submitReview() {
    var subjectId = document.getElementById("subject_id").value;
    var rating = document.getElementById("rating").value;
    var text = document.getElementById("review-text").value;
    var msgBox = document.getElementById("form-msg");

    // Basic client-side validation
    if (!subjectId) {
        showMsg(msgBox, "Please select a subject.", "error");
        return;
    }
    if (rating === "0") {
        showMsg(msgBox, "Please select a star rating.", "error");
        return;
    }
    if (text.trim().length < 20) {
        showMsg(msgBox, "Review must be at least 20 characters.", "error");
        return;
    }

    var formData = new FormData();
    formData.append("subject_id", subjectId);
    formData.append("rating", rating);
    formData.append("text", text);

    fetch("/submit-review", {
        method: "POST",
        body: formData
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            showMsg(msgBox, "Review submitted! Refreshing...", "success");
            setTimeout(function() { window.location.reload(); }, 1200);
        } else {
            showMsg(msgBox, data.error || "Something went wrong.", "error");
        }
    })
    .catch(function() {
        showMsg(msgBox, "Network error. Please try again.", "error");
    });
}

function showMsg(box, msg, type) {
    box.textContent = msg;
    box.className = "form-msg " + type;
    box.style.display = "block";
}

// ===== TEACHER DASHBOARD FUNCTIONS =====

// Toggle response form
function toggleForm(reviewId) {
    var form = document.getElementById("resp-form-" + reviewId);
    var btn = document.getElementById("btn-" + reviewId);
    if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
        if (btn) btn.style.display = "none";
    } else {
        form.style.display = "none";
        if (btn) btn.style.display = "inline-block";
    }
}

// Show edit form (when response already exists)
function showEditForm(reviewId, currentText) {
    var display = document.getElementById("resp-display-" + reviewId);
    var form = document.getElementById("resp-form-" + reviewId);
    var input = document.getElementById("resp-input-" + reviewId);
    if (display) display.style.display = "none";
    if (form) form.style.display = "block";
    if (input) input.value = currentText;
}

// Cancel edit (go back to display)
function cancelEdit(reviewId) {
    var display = document.getElementById("resp-display-" + reviewId);
    var form = document.getElementById("resp-form-" + reviewId);
    if (display) display.style.display = "block";
    if (form) form.style.display = "none";
}

// Submit or update a response
function submitResponse(reviewId) {
    var input = document.getElementById("resp-input-" + reviewId);
    var text = input ? input.value.trim() : "";

    if (text.length < 5) {
        alert("Response is too short. Please write at least 5 characters.");
        return;
    }

    var formData = new FormData();
    formData.append("response_text", text);

    fetch("/teacher/respond/" + reviewId, {
        method: "POST",
        body: formData
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.error || "Something went wrong.");
        }
    })
    .catch(function() {
        alert("Network error. Please try again.");
    });
}

// Delete a response
function deleteResponse(reviewId) {
    if (!confirm("Are you sure you want to delete this response?")) return;

    fetch("/teacher/respond/" + reviewId + "/delete", {
        method: "POST"
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            window.location.reload();
        } else {
            alert("Could not delete response.");
        }
    })
    .catch(function() {
        alert("Network error. Please try again.");
    });
}
