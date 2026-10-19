/* ==========================================================================
   JobNest – Client-side Interactive Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Navigation Toggle
  const mobileToggle = document.getElementById('mobileNavToggle');
  const navLinks = document.getElementById('navLinks');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }

  // 2. User Menu Dropdown Toggle
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userDropdownMenu = document.getElementById('userDropdownMenu');

  if (userMenuBtn && userDropdownMenu) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdownMenu.classList.toggle('show');
    });

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
      if (!userDropdownMenu.contains(e.target) && !userMenuBtn.contains(e.target)) {
        userDropdownMenu.classList.remove('show');
      }
    });
  }

  // 3. Flash Alert Dismiss Buttons
  const alertCloses = document.querySelectorAll('.alert-close');
  alertCloses.forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // Auto-dismiss success flash messages after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-success, .alert-info');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 400);
      }
    }, 6000);
  });

  // 4. Modal Dialog Handlers
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  };

  // Close modals when clicking on backdrop
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  // 5. File Upload Field Visual Preview & Feedback
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    input.addEventListener('change', () => {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        const fileName = file.name;
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        
        // Find text or status inside parent file-upload-box
        const uploadBox = input.closest('.file-upload-box');
        if (uploadBox) {
          const statusText = uploadBox.querySelector('.file-upload-status');
          if (statusText) {
            statusText.innerHTML = `<strong>Selected:</strong> ${fileName} (${fileSizeMB} MB)`;
            statusText.style.color = '#10b981';
          }
        }
      }
    });
  });

  // 6. Application Modal Resume Radio Toggle
  const resumeRadios = document.querySelectorAll('input[name="resume_choice"]');
  const customResumeUploadGroup = document.getElementById('customResumeGroup');

  if (resumeRadios.length > 0 && customResumeUploadGroup) {
    resumeRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        if (radio.value === 'new') {
          customResumeUploadGroup.style.display = 'block';
        } else {
          customResumeUploadGroup.style.display = 'none';
        }
      });
    });
  }

  // 7. Generic Confirmation on Destructive Actions
  const confirmForms = document.querySelectorAll('form[data-confirm]');
  confirmForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      const msg = form.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
});
