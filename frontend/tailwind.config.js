/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Spotify-inspired dark theme
        'spotify-black': '#121212',
        'spotify-dark': '#181818',
        'spotify-card': '#282828',
        'spotify-hover': '#2a2a2a',
        'spotify-green': '#1DB954',
        'spotify-green-hover': '#1ed760',
        
        // Gen-Z accent colors
        'neon-purple': '#a855f7',
        'neon-pink': '#ec4899',
        'neon-blue': '#3b82f6',
        'neon-cyan': '#06b6d4',
        
        // Text colors
        'text-primary': '#ffffff',
        'text-secondary': '#b3b3b3',
        'text-muted': '#727272',
      },
      fontFamily: {
        'display': ['Clash Display', 'system-ui', 'sans-serif'],
        'body': ['DM Sans', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'linear-gradient(135deg, #1DB954 0%, #191414 50%, #a855f7 100%)',
        'gradient-glow': 'linear-gradient(180deg, rgba(29, 185, 84, 0.15) 0%, transparent 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'bounce-subtle': 'bounceSubtle 2s infinite',
        'spin-slow': 'spin 8s linear infinite',
        'wave': 'wave 1.5s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(29, 185, 84, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(29, 185, 84, 0.6)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(1)' },
          '50%': { transform: 'scaleY(1.5)' },
        },
      },
      boxShadow: {
        'glow-green': '0 0 40px rgba(29, 185, 84, 0.3)',
        'glow-purple': '0 0 40px rgba(168, 85, 247, 0.3)',
        'card': '0 4px 60px rgba(0, 0, 0, 0.5)',
      },
    },
  },
  plugins: [],
}
