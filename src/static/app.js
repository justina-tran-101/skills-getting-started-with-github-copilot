document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Reset activity select (keep the default first option)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Main content
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants section
        const participantsDiv = document.createElement("div");
        participantsDiv.className = "participants";

        const participantsHeader = document.createElement("h5");
        participantsHeader.textContent = "Participants";
        participantsDiv.appendChild(participantsHeader);

        const participantsUl = document.createElement("ul");
        participantsUl.className = "participants-list";

        if (Array.isArray(details.participants) && details.participants.length > 0) {
          details.participants.forEach((p) => {
            const li = document.createElement("li");
            li.className = "participant-item";

            // support participant as object {email, first_name, last_name} or legacy string
            let email = "";
            let firstName = "";
            let lastName = "";
            if (typeof p === "string") {
              email = p;
              firstName = p.split("@")[0];
            } else if (typeof p === "object" && p !== null) {
              email = p.email || "";
              firstName = p.first_name || p.firstName || "";
              lastName = p.last_name || p.lastName || "";
            }

            // small badge showing first name (or local part) then full name + email
            const badge = document.createElement("span");
            badge.className = "participant-badge";
            badge.textContent = firstName || email.split("@")[0];

            const text = document.createElement("span");
            text.textContent = `${firstName} ${lastName}`.trim() + (firstName || lastName ? ` — ${email}` : email);

            // remove button
            const removeBtn = document.createElement("button");
            removeBtn.className = "participant-remove-btn";
            removeBtn.title = "Unregister participant";
            removeBtn.type = "button";
            removeBtn.innerHTML = "✖";

            // store data for handler
            removeBtn.dataset.activity = name;
            removeBtn.dataset.email = email;

            // click handler to unregister
            removeBtn.addEventListener("click", async (evt) => {
              // optimistic UI: disable button while processing
              removeBtn.disabled = true;
              try {
                const activityName = encodeURIComponent(removeBtn.dataset.activity);
                const emailParam = encodeURIComponent(removeBtn.dataset.email);
                const resp = await fetch(`/activities/${activityName}/participants?email=${emailParam}`, {
                  method: "DELETE",
                });

                const result = await resp.json();
                if (resp.ok) {
                  // reload activities to update availability and participants
                  fetchActivities();
                } else {
                  messageDiv.textContent = result.detail || result.message || "Failed to unregister";
                  messageDiv.className = "error";
                  messageDiv.classList.remove("hidden");
                  setTimeout(() => messageDiv.classList.add("hidden"), 5000);
                  removeBtn.disabled = false;
                }
              } catch (error) {
                console.error("Error unregistering:", error);
                messageDiv.textContent = "Failed to unregister. Please try again.";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
                setTimeout(() => messageDiv.classList.add("hidden"), 5000);
                removeBtn.disabled = false;
              }
            });

            li.appendChild(badge);
            li.appendChild(text);
            li.appendChild(removeBtn);
            participantsUl.appendChild(li);
          });
        } else {
          const li = document.createElement("li");
          li.className = "no-participants";
          li.textContent = "No participants yet";
          participantsUl.appendChild(li);
        }

        participantsDiv.appendChild(participantsUl);
        activityCard.appendChild(participantsDiv);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const firstName = document.getElementById("first-name").value.trim();
    const lastName = document.getElementById("last-name").value.trim();
    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    // Client-side validation: require names and @mergington.com domain
    if (!firstName) {
      messageDiv.textContent = "First name is required";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      setTimeout(() => messageDiv.classList.add("hidden"), 3000);
      return;
    }
    if (!lastName) {
      messageDiv.textContent = "Last name is required";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      setTimeout(() => messageDiv.classList.add("hidden"), 3000);
      return;
    }

    if (!email || !email.toLowerCase().trim().endsWith("@mergington.com")) {
      messageDiv.textContent = "Email must end with @mergington.com";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 4000);
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}&first_name=${encodeURIComponent(firstName)}&last_name=${encodeURIComponent(lastName)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // refresh activities so the new participant appears immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
