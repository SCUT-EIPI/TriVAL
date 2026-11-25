const filter = document.querySelector(".filter");
const query = document.querySelector("#type-query");
const records = [...document.querySelectorAll(".catalogue-scroll tbody tr")];
const count = document.querySelector("#match-count");

function filterTypes() {
  const term = query.value.trim().toLowerCase();
  let matches = 0;
  for (const row of records) {
    row.hidden = !row.querySelector("th").textContent.toLowerCase().includes(term);
    if (!row.hidden) matches++;
  }
  count.textContent = matches + (matches === 1 ? " problem type" : " problem types");
}

filter.hidden = false;
query.addEventListener("input", filterTypes);
filterTypes();

const copy = document.querySelector("#copy-cite");
const citation = document.querySelector("#bibtex");
const status = document.querySelector("#copy-status");
copy.hidden = false;
copy.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(citation.textContent);
    status.textContent = "Citation copied.";
  } catch {
    const range = document.createRange();
    range.selectNodeContents(citation);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = "Citation selected. Use your device’s copy command.";
  }
});
