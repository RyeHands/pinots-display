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

fetch('config.json?version=' + new Date().getTime())
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(config => {
    const artistFont = allowedFonts[config.fonts.artist_font] || "'Arial', sans-serif";
    const bartenderFont = allowedFonts[config.fonts.bartender_font] || "'Arial', sans-serif";
    const paintingFont = allowedFonts[config.fonts.painting_font] || "'Arial', sans-serif";
    
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

      #footer-bar {
        background-color: ${config.colors.footer_background};
      }
    `;

    document.getElementById('dynamic-styles').textContent = styles;

    const textColor = getLuminance(config.colors.footer_background) > 0.5 ? '#000000' : '#FFFFFF';
    document.getElementById('room').style.color = textColor;
    document.getElementById('current-time').style.color = textColor;
    document.getElementById('footer-bar').style.borderTop = getLuminance(config.colors.footer_background) > 0.5 ? '1px solid #ccc' : '1px solid #333'

    const titleElement = document.getElementById('painting-title');
    titleElement.textContent = config.painting_name;
    const textLength = config.painting_name.trim().length;
    let fontSize;
    if (textLength <= 10) {
        fontSize = '10vh';
    } else if (textLength <= 20) {
        fontSize = '8vh';
    } else if (textLength <= 35) {
        fontSize = '7vh';
    } else if (textLength <= 50) {
      fontSize = '6vh';
    } else {
        fontSize = '4vh';
    }
    titleElement.style.fontSize = fontSize;

    document.getElementById('artist-name').textContent = config.artist_name;
    document.getElementById('bartender-name').textContent = config.bartender_name;

    const paintingImage = document.querySelector('.painting-image');
    if (paintingImage && config.painting_source) {
      paintingImage.src = config.painting_source;
    }

    const bartenderContainer = document.querySelector('.bartender-container');
    if (bartenderContainer) {
      if (config.bartender_enabled) {
        bartenderContainer.style.display = '';
      } else {
        bartenderContainer.style.display = 'none';
      }
    }
  })
  .catch(err => {
    console.error('Error loading configuration:', err);
    document.body.innerHTML = "<h2>Error loading configuration. Please try again later.</h2>";
  });

fetch('room.txt?version=' + new Date().getTime())
  .then(response => {
    if (!response.ok) {
      throw new Error('room.txt missing');
    }
    return response.text();
  })
  .then(text => {
    document.getElementById('room').textContent = text.trim();
  })
  .catch(error => {
    console.warn(error);
    document.getElementById('room').textContent = "room.txt missing";
  });

function getLuminance(bgColor) {
  if (bgColor.startsWith('#')) bgColor = bgColor.slice(1);

  const r = parseInt(bgColor.substr(0, 2), 16);
  const g = parseInt(bgColor.substr(2, 2), 16);
  const b = parseInt(bgColor.substr(4, 2), 16);

  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  return luminance;
}

function updateTime() {
  const now = new Date();

  // 12-hour format
  let hours = now.getHours();
  let minutes = now.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';

  hours = hours % 12;
  hours = hours ? hours : 12;

  minutes = minutes < 10 ? '0' + minutes : minutes;
  const timeString = `${hours}:${minutes} ${ampm}`;

  document.getElementById('current-time').textContent = timeString;
}

updateTime();

setInterval(updateTime, 60000);