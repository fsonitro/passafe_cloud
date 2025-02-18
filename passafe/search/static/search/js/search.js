function filterDashboard() {
    const query = document.getElementById("search-bar").value.toLowerCase();

    // Filter ungrouped entries
    const rows = document.querySelectorAll("#entries-tbody tr");
    rows.forEach(row => {
        const searchableFields = row.querySelectorAll(".searchable");
        const matches = Array.from(searchableFields).some(field =>
            field.textContent.toLowerCase().includes(query)
        );
        row.style.display = matches ? "" : "none";
    });

    // Filter folders
    const folders = document.querySelectorAll(".folder-container");
    folders.forEach(folder => {
        const folderName = folder.getAttribute("data-folder-name").toLowerCase();
        const folderEntries = folder.querySelectorAll(".folder-entries-tbody tr");

        // Check if folder name matches
        const folderNameMatches = folderName.includes(query);

        // Check if any entries inside the folder match
        let entryMatches = false;
        folderEntries.forEach(entry => {
            const entryFields = entry.querySelectorAll(".searchable");
            const matches = Array.from(entryFields).some(field =>
                field.textContent.toLowerCase().includes(query)
            );
            entry.style.display = matches ? "" : "none";
            if (matches) {
                entryMatches = true;
            }
        });

        // Show folder if folder name matches or any entries match
        folder.style.display = folderNameMatches || entryMatches ? "" : "none";
    });
}
