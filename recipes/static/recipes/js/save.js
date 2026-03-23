function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

document.addEventListener("click", async function (event) {
  const button = event.target.closest(".save-btn");
  if (!button) return;

  event.preventDefault();

  const url = button.dataset.url;
  const recipeId = button.dataset.recipeId;
  const csrftoken = getCookie("csrftoken");

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest"
      }
    });

    if (!response.ok) {
      throw new Error("Request failed");
    }

    const data = await response.json();

    button.textContent = data.saved ? "Unsave" : "Save";

    const count = document.getElementById(`save-count-${recipeId}`);
    if (count) {
      count.textContent = data.save_count;
    }
  } catch (error) {
    console.error("Save AJAX failed:", error);
  }
});