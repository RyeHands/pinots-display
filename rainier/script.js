// Define the list of allowed fonts
const allowedFonts = {
  "Roboto": "'Roboto', sans-serif",
  "Slabo 27px": "'Slabo 27px', serif",
  "Delius": "'Delius', cursive",
  "Borel": "'Borel', cursive",
  "Chewy": "'Chewy', system-ui",
  "Parisienne": "'Parisienne', cursive",
  "Barriecito": "'Barriecito', system-ui",
  "Bangers": "'Bangers', system-ui",
  "Caveat": "'Caveat', cursive",
  "DM Serif Text": "'DM Serif Text', serif"
};

// Fetch the configuration JSON file
fetch('config.json?version=' + new Date().getTime()) // Cache-busting query parameter
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(config => {
    // Validate fonts from config and get full font stack
    const artistFont = allowedFonts[config.fonts.artist_font] || "'Arial', sans-serif";
    const bartenderFont = allowedFonts[config.fonts.bartender_font] || "'Arial', sans-serif";
    const paintingFont = allowedFonts[config.fonts.painting_font] || "'Arial', sans-serif";
    
    // Set dynamic styles using data from the config
    const styles = `
      body {
        background-color: ${config.colors.background_color};
      }

      .painting-title {
        color: ${config.colors.title_color};
        font-family: ${paintingFont};
      }

      .artist {
        color: ${config.colors.artist_color};
        font-family: ${artistFont};
      }

      .bartender {
        color: ${config.colors.bartender_color};
        font-family: ${bartenderFont};
      }

      .label {
        color: ${config.colors.label_color};
      }

      .left-panel {
        background-color: ${config.colors.panel_background};
      }
    `;

    // Inject the styles into the page
    document.getElementById('dynamic-styles').textContent = styles;

    // Populate content dynamically
    document.getElementById('painting-title').textContent = config.painting_name;
    document.getElementById('artist-name').textContent = config.artist_name;
    document.getElementById('bartender-name').textContent = config.bartender_name;

    // Dynamically set the image source from config.painting_source
    const paintingImage = document.querySelector('.painting-image');
    if (paintingImage && config.painting_source) {
      paintingImage.src = config.painting_source; // Set the image source from the config
    }

    const bartenderContainer = document.getElementById('bartender-container');
    if (bartenderContainer) {
      if (config.bartender_enabled === false) {
        bartenderContainer.style.display = 'none';
      } else {
        bartenderContainer.style.display = ''; // show it if enabled or undefined
      }
    }

    // Function to update the current time
    function updateTime() {
      const now = new Date();

      // 12-hour format
      let hours = now.getHours();
      let minutes = now.getMinutes();
      const ampm = hours >= 12 ? 'PM' : 'AM';

      // Convert hours to 12-hour format
      hours = hours % 12;
      hours = hours ? hours : 12; // 0 becomes 12

      // Add leading zero to minutes and seconds if necessary
      minutes = minutes < 10 ? '0' + minutes : minutes;
      const timeString = `${hours}:${minutes} ${ampm}`;

      // Update the time in the footer
      document.getElementById('current-time').textContent = timeString;
    }

    // Initial time update
    updateTime();

    // Update time every 60 seconds (1 minute)
    setInterval(updateTime, 60000);
  })
  .catch(err => {
    console.error('Error loading configuration:', err);
    // Optionally, show an error message on the page if config loading fails
    document.body.innerHTML = "<h2>Error loading configuration. Please try again later.</h2>";
  });
