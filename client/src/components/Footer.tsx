export default function Footer() {
  return (
    <footer className="bg-zinc-900 border-t border-zinc-800 py-6 text-center text-zinc-500 text-sm">
      <p>&copy; {new Date().getFullYear()} Countrydle. All rights reserved.</p>
      <div className="mt-2 flex justify-center gap-4">
        <a href="#" className="hover:text-zinc-300 transition-colors">Privacy Policy</a>
        <a href="#" className="hover:text-zinc-300 transition-colors">Terms of Service</a>
      </div>
    </footer>
  );
}
