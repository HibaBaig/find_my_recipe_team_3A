function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

document.addEventListener("click", async (e) => {
  if (!e.target.classList.contains("save-btn")) return;

  const recipeId = e.target.dataset.recipeId;
  const csrftoken = getCookie("csrftoken");

  const res = await fetch(`/recipes/${recipeId}/toggle-save/`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
  });

  const data = await res.json();

  e.target.textContent = data.saved ? "Saved ✓" : "Save";
  document.getElementById(`save-count-${recipeId}`).textContent = data.save_count;
});