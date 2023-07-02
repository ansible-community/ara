/* Inspired by https://getbootstrap.com/docs/5.3/customize/color-modes/#javascript */
/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2023 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

const getStoredTheme = () => localStorage.getItem('theme')
const setStoredTheme = theme => localStorage.setItem('theme', theme)

const getPreferredTheme = () => {
  const storedTheme = getStoredTheme()
  if (storedTheme) {
    return storedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const setTheme = theme => {
  if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
  } else {
    document.documentElement.setAttribute('data-bs-theme', theme)
    document.getElementById('dark-light-toggle-btn').setAttribute('checked', 'true')
  }
  if (theme === 'light') {
    document.getElementById('dark-light-toggle-btn').removeAttribute('checked')
    document.getElementById("pygments-dark-css").disabled = true;
    document.getElementById("pygments-light-css").disabled = false;
  } else {
    document.getElementById('dark-light-toggle-btn').setAttribute('checked', 'true')
    document.getElementById("pygments-dark-css").disabled = false;
    document.getElementById("pygments-light-css").disabled = true;
  }
}

setTheme(getPreferredTheme())

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  const storedTheme = getStoredTheme()
  if (storedTheme !== 'light' && storedTheme !== 'dark') {
    setTheme(getPreferredTheme())
  }
})

document.getElementById('dark-light-toggle-btn').addEventListener('click',()=>{
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
      setTheme('light')
      setStoredTheme('light')
    }
    else {
      setTheme('dark')
      setStoredTheme('dark')
    }
})
