// ===== VCET Review System — main.js =====

// Star picker logic
var selectedRating = 0;

var starPicker = document.getElementById("starPicker");
if (starPicker) {
    var stars = starPicker.querySelectorAll(".star");

    stars.forEach(function(star) {
        star.addEventListener("mouseover", function() {
            var val = parseInt(this.getAttribute("data-val"));
            highlightStars(val);
        });
        star.addEventListener("mouseout", function() {
            highlightStars(selectedRating);
        });
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
        charCount.style.color = len > 450 ? "#e74c3c" : "";
    });
}

// ===== LOAD REVIEWS FROM API =====
function renderStars(rating) {
    var html = '';
    for (var i = 1; i <= 5; i++) {
        html += i <= rating
            ? '<span class="star-filled">★</span>'
            : '<span class="star-empty">★</span>';
    }
    return html;
}

function loadReviews() {
    var feed = document.getElementById("reviewFeed");
    var topBox = document.getElementById("topReviewBox");

    // Load all reviews
    if (feed) {
        fetch("/api/reviews")
            .then(function(res) { return res.json(); })
            .then(function(reviews) {
                if (!reviews || reviews.length === 0) {
                    feed.innerHTML = '<div class="empty-state">No reviews yet. Be the first to share your feedback!</div>';
                    return;
                }
                feed.innerHTML = reviews.map(function(r) {
                    var responseHtml = r.response
                        ? '<div class="faculty-response"><span class="response-label">Faculty Response:</span><p>' + r.response.text + '</p></div>'
                        : '';
                    return '<div class="review-card fade-in">' +
                        '<div class="review-top">' +
                            '<span class="review-subject">' + r.subject + '</span>' +
                            '<span class="stars-display">' + renderStars(r.rating) + '</span>' +
                        '</div>' +
                        '<p class="review-text">' + r.text + '</p>' +
                        '<div class="review-meta">' +
                            '<span class="anon-label">Anonymous Student</span>' +
                            '<span class="review-time">' + r.created_at + '</span>' +
                        '</div>' +
                        responseHtml +
                    '</div>';
                }).join('');
            })
            .catch(function() {
                feed.innerHTML = '<div class="empty-state">Could not load reviews. Please refresh.</div>';
            });
    }

    // Load top review
    if (topBox) {
        fetch("/api/top-review")
            .then(function(res) { return res.json(); })
            .then(function(r) {
                if (!r) {
                    topBox.innerHTML = '<div class="empty-state">No reviews yet!</div>';
                    return;
                }
                var responseHtml = r.response
                    ? '<div class="faculty-response"><span class="response-label">Faculty Response:</span><p>' + r.response.text + '</p></div>'
                    : '';
                topBox.innerHTML =
                    '<div class="spotlight-card">' +
                        '<div class="spotlight-badge">TOP RATED</div>' +
                        '<div class="spotlight-subject">' + r.subject + '</div>' +
                        '<div class="spotlight-stars">' + renderStars(r.rating) + '</div>' +
                        '<p class="spotlight-text">"' + r.text + '"</p>' +
                        '<div class="spotlight-meta">' +
                            '<span>Anonymous Student</span>' +
                            '<span>' + r.created_at + '</span>' +
                        '</div>' +
                        responseHtml +
                    '</div>';
            })
            .catch(function() {
                if (topBox) topBox.innerHTML = '<div class="empty-state">Could not load top review.</div>';
            });
    }
}

// Run on student portal page
if (document.getElementById("reviewFeed") || document.getElementById("topReviewBox")) {
    loadReviews();
}

// ===== SUBMIT REVIEW =====
function submitReview() {
    var subjectId = document.getElementById("subject_id").value;
    var rating = document.getElementById("rating").value;
    var text = document.getElementById("review-text").value;
    var msgBox = document.getElementById("form-msg");

    if (!subjectId) { showMsg(msgBox, "Please select a subject.", "error"); return; }
    if (rating === "0") { showMsg(msgBox, "Please select a star rating.", "error"); return; }
    if (text.trim().length < 20) { showMsg(msgBox, "Review must be at least 20 characters.", "error"); return; }

    var formData = new FormData();
    formData.append("subject_id", subjectId);
    formData.append("rating", rating);
    formData.append("text", text);

    fetch("/submit-review", { method: "POST", body: formData })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                showMsg(msgBox, "Review submitted! Refreshing...", "success");
                setTimeout(function() { window.location.reload(); }, 1200);
            } else {
                showMsg(msgBox, data.error || "Something went wrong.", "error");
            }
        })
        .catch(function() { showMsg(msgBox, "Network error. Please try again.", "error"); });
}

function showMsg(box, msg, type) {
    box.textContent = msg;
    box.className = "form-msg " + type;
    box.style.display = "block";
}

// ===== MODAL (Write a Review button) =====
function openModal() {
    var modal = document.getElementById("reviewModal");
    if (modal) modal.style.display = "flex";
}

function closeModal() {
    var modal = document.getElementById("reviewModal");
    if (modal) modal.style.display = "none";
}

// Close modal on background click
document.addEventListener("click", function(e) {
    var modal = document.getElementById("reviewModal");
    if (modal && e.target === modal) closeModal();
});

// ===== TEACHER DASHBOARD FUNCTIONS =====

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

function showEditForm(reviewId, currentText) {
    var display = document.getElementById("resp-display-" + reviewId);
    var form = document.getElementById("resp-form-" + reviewId);
    var input = document.getElementById("resp-input-" + reviewId);
    if (display) display.style.display = "none";
    if (form) form.style.display = "block";
    if (input) input.value = currentText;
}

function cancelEdit(reviewId) {
    var display = document.getElementById("resp-display-" + reviewId);
    var form = document.getElementById("resp-form-" + reviewId);
    if (display) display.style.display = "block";
    if (form) form.style.display = "none";
}

// FIX: Send JSON instead of FormData (app.py uses request.get_json())
function submitResponse(reviewId) {
    var input = document.getElementById("resp-input-" + reviewId);
    var text = input ? input.value.trim() : "";

    if (text.length < 5) {
        alert("Response is too short. Please write at least 5 characters.");
        return;
    }

    fetch("/teacher/respond/" + reviewId, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })   // ← was FormData, now JSON
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) { window.location.reload(); }
        else { alert(data.error || "Something went wrong."); }
    })
    .catch(function() { alert("Network error. Please try again."); });
}

// FIX: Use DELETE method instead of wrong /delete URL
function deleteResponse(reviewId) {
    if (!confirm("Are you sure you want to delete this response?")) return;

    fetch("/teacher/respond/" + reviewId, {
        method: "DELETE"   // ← was POST to /delete, now DELETE to same URL
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) { window.location.reload(); }
        else { alert("Could not delete response."); }
    })
    .catch(function() { alert("Network error. Please try again."); });
}
