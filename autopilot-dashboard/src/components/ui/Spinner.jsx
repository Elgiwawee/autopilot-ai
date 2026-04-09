// src/components/ui/Spinner.jsx

export default function Spinner() {
  return (
    <div className="flex justify-center items-center h-40">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary" />
    </div>
  );
}
