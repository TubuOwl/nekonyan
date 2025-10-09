async function loadData() {
  const gallery = document.getElementById('gallery');
  gallery.innerHTML = '<p>Scraping 1–10 pages...</p>';

  try {
      const res = await fetch('/scrape');
      const data = await res.json();

      gallery.innerHTML = '';
      data.forEach(item => {
          gallery.innerHTML += `
              <div class="card" onclick="showDetail('${item.link}', '${item.title}', '${item.image}')">
                  <img src="${item.image}" 
                       onerror="this.src='https://via.placeholder.com/180x120?text=No+Image'">
                  <div class="info">${item.title}</div>
              </div>
          `;
      });
  } catch (err) {
      gallery.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
  }
}

async function showDetail(link, title, image) {
  const box = document.getElementById('details');
  box.style.display = 'block';
  box.innerHTML = '<p>Loading detail...</p>';

  try {
      const res = await fetch('/detail?link=' + encodeURIComponent(link));
      const d = await res.json();

      let videoHtml = '';
      if (d.streams && d.streams.length > 0) {
          videoHtml = d.streams.map((src, i) => `
              <div id="stream${i + 1}" class="openstream">
                  <iframe src="${src}" scrolling="no" frameborder="0"
                      width="100%" height="430" sandbox="allow-scripts allow-same-origin" referrerpolicy="no-referrer" allow="clipboard-read; clipboard-write"      allowfullscreen></iframe>
              </div>
          `).join('');
      } else {
          videoHtml = '<p style="color:red;">No streams found.</p>';
      }

      box.innerHTML = `
          <h2>${title}</h2>
          ${videoHtml}
          <p><strong>Genre:</strong> ${d.genre || '-'}</p>
          <p><strong>Producers:</strong> ${d.producers || '-'}</p>
          <p><strong>Duration:</strong> ${d.duration || '-'}</p>
          <p><strong>Size:</strong> ${d.size || '-'}</p>
          <p><strong>Note:</strong> ${d.note || '-'}</p>
          <p><strong>Sinopsis:</strong><br>${d.sinopsis || '-'}</p>
      `;

      box.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
      box.innerHTML = `<p style="color:red;">Failed to load detail: ${err.message}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', loadData);
