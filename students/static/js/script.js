// Sidebar active highlight
document.querySelectorAll(".sidebar a").forEach(link => {
    link.addEventListener("click", function () {
        document.querySelectorAll(".sidebar a").forEach(l => l.classList.remove("active"));
        this.classList.add("active");
    });
});

// Smooth fade-in animation
window.onload = function () {
    document.body.style.opacity = "1";
};

// Alert on add student
function showSuccess() {
    alert("🎉 Student Added Successfully!");
}