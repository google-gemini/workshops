<template>
  <div :id="containerId" class="w-full h-auto"></div> <!-- Added class for responsive sizing -->
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps({
  svgFile: {
    type: String,
    required: true,
  },
})

// Create a unique ID for each component instance
const containerId = ref(`svg-container-${Math.random().toString(36).substr(2, 9)}`)

// Function to trigger the animation
function animateSVG(svgFile: string, containerId: string) {
  fetch(svgFile)
    .then((response) => response.text())
    .then((svgContent) => {
      document.getElementById(containerId).innerHTML = svgContent

      const svgElement = document.querySelector(`#${containerId} svg`)
      svgElement.style.width = "100%"
      svgElement.style.height = "auto"
      svgElement.style.overflow = "visible"

      const allPaths = svgElement.querySelectorAll("path")
      allPaths.forEach((path) => {
        const length = path.getTotalLength()
        path.style.strokeDasharray = length
        path.style.strokeDashoffset = length
      })

      const pathsWithoutStroke = Array.from(svgElement.querySelectorAll('path')).filter(
        (path) => {
          const hasStrokeInStyle =
            window.getComputedStyle(path).stroke !== 'none' &&
            window.getComputedStyle(path).stroke !== ''
          return !hasStrokeInStyle
        }
      )

      gsap.set(pathsWithoutStroke, { opacity: 0 }) // Set initial opacity to 0

      // Simple GSAP animation without ScrollTrigger
      allPaths.forEach((path) => {
        gsap.to(path, {
          strokeDashoffset: 0,
          duration: 10,
          ease: 'power1.inOut',
          stagger: 0.2,
        })
      })

      gsap.fromTo(
        allPaths,
        { opacity: 0 },
        { opacity: 1, duration: 10, ease: 'power1.out' }
      )
    })
    .catch((error) => console.error('Error loading the SVG:', error))
}

// MutationObserver to detect when the class changes
function observeSlideVisibility(containerId: string) {
  const figureElement = document.querySelector(`#${containerId}`).closest('figure')

  if (!figureElement) {
    console.error('Figure element not found!')
    return
  }

  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'class') {
        const currentClass = figureElement.className
        if (currentClass.includes('slidev-vclick-current')) {
          console.log('Slide is visible, triggering animation')
          animateSVG(props.svgFile, containerId)
          observer.disconnect() // Stop observing after the animation is triggered
        }
      }
    })
  })

  observer.observe(figureElement, {
    attributes: true, // Watch for attribute changes (like class)
    attributeFilter: ['class'], // Only monitor the class attribute
  })
}

// Trigger the observer on mount
onMounted(() => {
  observeSlideVisibility(containerId.value)
})
</script>
