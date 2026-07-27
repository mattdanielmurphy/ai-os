// ==UserScript==
// @name         LiveBench Efficient Frontier Highlight
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Highlight efficient frontier on LiveBench by striking through rows with no new performance peaks
// @author       You
// @match        https://livebench.ai/*
// @grant        none
// ==/UserScript==

(function() {
  let observer;

  function run() {
    // 1. Temporarily disconnect to avoid infinite loop from our own modifications
    if (observer) {
      observer.disconnect();
    }

    try {
      const rows = Array.from(document.querySelectorAll('tr.row'));
      if (rows.length === 0) return;

      const colCount = rows[0].cells.length;

      // 1. Identify specific column types
      const performanceColumnIndices = [];
      let costColumnIdx = -1;

      for (let c = 0; c < colCount; c++) {
        const cell = rows[0].cells[c];
        // Clone the cell and remove any existing delta spans to get clean text
        const clone = cell.cloneNode(true);
        const deltas = clone.querySelectorAll('.delta-value');
        deltas.forEach(d => d.remove());
        const text = clone.textContent.trim();
        const cleanNum = text.replace(/[^\d.-]/g, '');
        
        const hasNumbers = !isNaN(parseFloat(cleanNum)) && cleanNum.length > 0;
        const isCost = text.includes('$') || cell.classList.contains('lb-cost-col');
        const isName = /[a-zA-Z]/.test(text) && !isCost;

        if (hasNumbers && !isName) {
          if (isCost) {
            costColumnIdx = c;
          } else {
            performanceColumnIndices.push(c);
          }
        }
      }

      // 2. Calculate peaks and apply formatting
      const columnMaxes = new Array(colCount).fill(-Infinity);

      rows.forEach((row) => {
        let rowHasNewPeak = false;

        Array.from(row.cells).forEach((cell, c) => {
          // Remove any existing delta spans first
          const existingDelta = cell.querySelector('.delta-value');
          if (existingDelta) existingDelta.remove();

          if (performanceColumnIndices.includes(c)) {
            const val = parseFloat(cell.textContent.trim().replace(/[^\d.-]/g, ''));
            if (!isNaN(val)) {
              const prevMax = columnMaxes[c];
              
              if (val >= prevMax) {
                // New peak or equal to peak
                if (prevMax !== -Infinity && val > prevMax) {
                  const delta = (val - prevMax).toFixed(0);
                  const deltaSpan = document.createElement('span');
                  deltaSpan.className = 'delta-value';
                  deltaSpan.textContent = ` +${delta}`;
                  deltaSpan.style.cssText = 'font-size: 0.75em; font-weight: 400; color: #2ecc71; margin-left: 4px; display: inline-block;';
                  cell.appendChild(deltaSpan);
                }
                
                columnMaxes[c] = val;
                cell.style.setProperty('font-weight', '900', 'important');
                cell.style.setProperty('color', '#000', 'important');
                rowHasNewPeak = true;
              } else {
                // Not a peak - show negative delta
                const delta = (val - prevMax).toFixed(0);
                const deltaSpan = document.createElement('span');
                deltaSpan.className = 'delta-value';
                deltaSpan.textContent = ` ${delta}`; // (e.g. -5)
                deltaSpan.style.cssText = 'font-size: 0.75em; font-weight: 400; color: #e74c3c; margin-left: 4px; display: inline-block;';
                cell.appendChild(deltaSpan);

                cell.style.setProperty('font-weight', '300', 'important');
                cell.style.setProperty('color', '#aaa', 'important');
              }
            }
          } 
          else {
            cell.style.setProperty('font-weight', '300', 'important');
            if (c === costColumnIdx) cell.style.setProperty('color', '#666', 'important');
          }
        });

        // 3. Strike through rows that offer no new performance peaks
        if (!rowHasNewPeak) {
          row.style.setProperty('text-decoration', 'line-through', 'important');
          row.style.setProperty('opacity', '0.4', 'important');
          row.style.setProperty('filter', 'grayscale(1)', 'important');
        } else {
          row.style.setProperty('text-decoration', 'none', 'important');
          row.style.setProperty('opacity', '1', 'important');
          row.style.setProperty('filter', 'none', 'important');
        }
      });
    } finally {
      // Re-observe
      if (observer) {
        observer.observe(document.body, { childList: true, subtree: true });
      }
    }
  }

  // Setup observer
  observer = new MutationObserver((mutations) => {
    // Only run if table rows are present on the page
    const hasRows = document.querySelector('tr.row');
    if (hasRows) {
      run();
    }
  });

  // Initial check
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      observer.observe(document.body, { childList: true, subtree: true });
      run();
    });
  } else {
    observer.observe(document.body, { childList: true, subtree: true });
    run();
  }
})();
