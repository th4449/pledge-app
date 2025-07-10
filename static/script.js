document.addEventListener("DOMContentLoaded", () => {
    // Get all the elements we'll need to work with
    const btnFindCompanies = document.getElementById("btn-find-companies");
    const companyListContainer = document.getElementById("company-list-container");
    const companySelect = document.getElementById("company-select");
    const btnResetMemory = document.getElementById("btn-reset-memory");

    const step2 = document.getElementById("step2");
    const step2b = document.getElementById("step2b");
    const step3 = document.getElementById("step3");
    const step4 = document.getElementById("step4");

    const spinnerInvestigate = document.getElementById("spinner-investigate");
    const investigationDetails = document.getElementById("investigation-details");

    const btnGenerateContent = document.getElementById("btn-generate-content");
    const resultsSection = document.getElementById("results-section");
    const resultsOutput = document.getElementById("results-output");
    const spinnerGenerate = document.getElementById("spinner-generate");

    let companyData = {};

    // --- Event listener for the RESET button ---
    btnResetMemory.addEventListener("click", async () => {
        if (confirm("Are you sure you want to reset the list of researched companies?")) {
            try {
                await fetch("/reset_memory", { method: "POST" });
                alert("Memory reset successfully. The next search will include all companies again.");
                // Hide all steps and results to start fresh
                companyListContainer.classList.add("hidden");
                step2.classList.add("hidden");
                step2b.classList.add("hidden");
                step3.classList.add("hidden");
                step4.classList.add("hidden");
                resultsSection.classList.add("hidden");
            } catch (error) {
                alert("Failed to reset memory. Check server logs.");
                console.error("Reset Error:", error);
            }
        }
    });

    // --- Event listener for finding companies ---
    // THIS FUNCTION IS NOW SIMPLIFIED
    btnFindCompanies.addEventListener("click", async () => {
        // Hide all subsequent steps to ensure a clean start
        resultsSection.classList.add("hidden");
        step2.classList.add("hidden");
        step2b.classList.add("hidden");
        step3.classList.add("hidden");
        step4.classList.add("hidden");
        
        btnFindCompanies.disabled = true;
        btnFindCompanies.textContent = "Finding...";
        companyListContainer.classList.add("hidden");

        try {
            const response = await fetch("/generate_initial_list", { method: "POST" });
            const data = await response.json();
            
            companySelect.innerHTML = "<option value=''>-- Select a Company to Investigate --</option>";
            companyData = {};

            if (data.companies.length === 0) {
                 alert("Could not find any new companies. Please try resetting the memory.");
                 return;
            }

            data.companies.forEach((companyInfo, index) => {
                const parts = companyInfo.split('||');
                const companyName = parts[0].trim();
                const option = document.createElement("option");
                option.value = index; 
                option.textContent = companyName;
                companySelect.appendChild(option);
                companyData[index] = { name: companyName, fullInfo: companyInfo };
            });

            // This button's ONLY job is to show the list.
            // The investigation is now triggered ONLY by a manual user selection.
            companyListContainer.classList.remove("hidden");

        } catch (error) {
            alert("Error finding companies. Check the server logs.");
            console.error("Error:", error);
        } finally {
            btnFindCompanies.disabled = false;
            btnFindCompanies.textContent = "Find New Companies";
        }
    });

    // --- Event listener for when a company is manually selected ---
    companySelect.addEventListener("change", async () => {
        const selectedIndex = companySelect.value;
        // This check is important. If the user selects the placeholder, do nothing.
        if (!selectedIndex || selectedIndex === "") {
            step2b.classList.add("hidden");
            step2.classList.add("hidden");
            step3.classList.add("hidden");
            step4.classList.add("hidden");
            return;
        }
        
        const selectedCompany = companyData[selectedIndex];
        if (!selectedCompany) return;

        step2b.classList.remove("hidden");
        spinnerInvestigate.classList.remove("hidden");
        investigationDetails.textContent = `Investigating ${selectedCompany.name}...`;
        
        // Hide other steps until investigation is complete
        step2.classList.add("hidden");
        step3.classList.add("hidden");
        step4.classList.add("hidden");

        try {
            const response = await fetch("/investigate_company", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ company: selectedCompany.name }),
            });
            const data = await response.json();
            investigationDetails.textContent = data.details;

            // Now show the rest of the steps
            step2.classList.remove("hidden");
            step3.classList.remove("hidden");
            step4.classList.remove("hidden");

        } catch (error) {
            investigationDetails.textContent = "Error during investigation. Check server logs.";
            console.error("Error:", error);
        } finally {
            spinnerInvestigate.classList.add("hidden");
        }
    });

    // --- Event listener for the final "Generate Content" button ---
    btnGenerateContent.addEventListener("click", async () => {
        const selectedIndex = companySelect.value;
        const selectedCompany = companyData[selectedIndex];
        const researchInput = document.getElementById("research-input").value;
        const marketInput = document.getElementById("market-input").value;
        const languageInput = document.getElementById("language-input").value;
        const connectionDetails = investigationDetails.textContent;

        if (!selectedCompany || !researchInput || !marketInput || !languageInput) {
            alert("Please fill out all fields before generating content.");
            return;
        }

        resultsSection.classList.remove("hidden");
        spinnerGenerate.classList.remove("hidden");
        resultsOutput.textContent = "";
        btnGenerateContent.disabled = true;

        try {
            const response = await fetch("/generate_content", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    company: selectedCompany.name,
                    connectionDetails: connectionDetails,
                    research: researchInput,
                    market: marketInput,
                    language: languageInput,
                }),
            });
            const data = await response.json();
            resultsOutput.textContent = data.content;
        } catch (error) {
            resultsOutput.textContent = "Error generating content. Check server logs.";
            console.error("Error:", error);
        } finally {
            spinnerGenerate.classList.add("hidden");
            btnGenerateContent.disabled = false;
        }
    });
});