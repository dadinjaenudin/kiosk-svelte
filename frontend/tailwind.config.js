/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: '#FF6B35',
				secondary: '#F7931E',
				accent: '#004E89',
				neutral: '#1A1A1D',
				'base-100': '#FFFFFF'
			},
			fontSize: {
				'kiosk-sm': '1.125rem',  // 18px
				'kiosk-base': '1.25rem', // 20px
				'kiosk-lg': '1.5rem',    // 24px
				'kiosk-xl': '2rem',      // 32px
				'kiosk-2xl': '2.5rem',   // 40px
				'kiosk-3xl': '3rem'      // 48px
			},
			spacing: {
				'touch': '64px',  // Minimum touch target
				'kiosk': '96px'   // Large kiosk buttons
			}
		}
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: [
			{
				light: {
					'primary': '#FF6B35',
					'secondary': '#F7931E',
					'accent': '#004E89',
					'neutral': '#1A1A1D',
					'base-100': '#FFFFFF',
					'info': '#3ABFF8',
					'success': '#36D399',
					'warning': '#FBBD23',
					'error': '#F87272'
				}
			}
		]
	}
};
