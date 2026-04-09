import { FaLinkedinIn, FaXTwitter, FaYoutube, FaInstagram } from "react-icons/fa6"

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-border bg-white mt-20">

      <div className="max-w-7xl mx-auto px-6 py-10">

        {/* TOP */}
        <div className="flex flex-col md:flex-row justify-between items-start gap-10">

          {/* LEFT */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Autopilot AI
            </h2>
            <p className="mt-3 text-sm text-gray-500 max-w-md">
              Autonomous cloud optimization that continuously reduces cost,
              enforces policies, and delivers real savings — without guesswork.
            </p>
          </div>

          {/* RIGHT */}
          <div>
            <p className="text-sm text-gray-600 mb-3">Follow Us</p>

            <div className="flex gap-3">
              {[FaLinkedinIn, FaXTwitter, FaYoutube, FaInstagram].map(
                (Icon, i) => (
                  <a
                    key={i}
                    href="#"
                    className="w-9 h-9 flex items-center justify-center rounded-md 
                               bg-gray-100 border border-gray-200
                               hover:bg-primary hover:text-white
                               transition duration-300"
                  >
                    <Icon size={14} />
                  </a>
                )
              )}
            </div>
          </div>
        </div>

        {/* BOTTOM */}
        <div className="border-t border-gray-200 mt-8 pt-5 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-gray-500">

          <div className="flex gap-5">
            <a href="#" className="hover:text-gray-900 transition">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-gray-900 transition">
              Terms Of Use
            </a>
          </div>

          <p>© {year} Autopilot AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}