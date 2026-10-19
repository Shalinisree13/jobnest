/* ==========================================================================
   JobNest – Dashboard Chart Initializers
   Uses Chart.js library
   ========================================================================== */

function initAdminCharts(statusData, categoryData) {
  // 1. Application Status Doughnut Chart
  const statusCtx = document.getElementById('adminStatusChart');
  if (statusCtx && statusData) {
    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(statusData),
        datasets: [{
          data: Object.values(statusData),
          backgroundColor: [
            '#f59e0b', // Under Review (warning)
            '#0284c7', // Shortlisted (info)
            '#2563eb', // Interview Scheduled (primary)
            '#10b981', // Hired (success)
            '#ef4444', // Rejected (danger)
            '#94a3b8'  // Withdrawn (secondary)
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Job Distribution By Category Bar Chart
  const catCtx = document.getElementById('adminCategoryChart');
  if (catCtx && categoryData) {
    new Chart(catCtx, {
      type: 'bar',
      data: {
        labels: categoryData.labels,
        datasets: [{
          label: 'Open Positions',
          data: categoryData.counts,
          backgroundColor: '#3b82f6',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: { family: "'Plus Jakarta Sans', sans-serif" } },
            grid: { color: '#f1f5f9' }
          },
          x: {
            ticks: { font: { family: "'Plus Jakarta Sans', sans-serif" }, maxRotation: 45, minRotation: 0 },
            grid: { display: false }
          }
        }
      }
    });
  }
}
