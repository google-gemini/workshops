<!--
 Copyright 2024 -l

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->


<template>
  <!-- Removed 'h-auto' since 'fixed-height' should define the height -->
  <div :id="containerId" class="svg-container w-full"></div>
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
      // Inject SVG content
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

      // GSAP animation for paths
      allPaths.forEach((path) => {
        gsap.to(path, {
          strokeDashoffset: 0,
          duration: 10,
          ease: 'power1.inOut',
          stagger: 0.2,
        })
      })

      // Fade in all paths
      gsap.fromTo(
        allPaths,
        { opacity: 0 },
        { opacity: 1, duration: 10, ease: 'power1.out' }
      )
    })
    .catch((error) => console.error('Error loading the SVG:', error))
}

// MutationObserver to detect when the slide becomes visible
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
