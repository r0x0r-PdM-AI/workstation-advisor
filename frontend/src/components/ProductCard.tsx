type ProductCardProps = {
  product: string;
  brand: string;
  form_factor: string;
  notes: string;
  rank: number;
  explanation?: string;
};

export default function ProductCard({
  product,
  brand,
  form_factor,
  notes,
  rank,
  explanation,
}: ProductCardProps) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900 p-5 text-white sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="break-words text-base font-semibold leading-6 tracking-tight text-white sm:text-lg sm:leading-7">
            {product} — {brand}
          </h3>
          <p className="mt-1 text-sm leading-5 text-gray-400">
            {form_factor}
          </p>
        </div>

        <span className="w-fit shrink-0 rounded-full border border-gray-700 px-2.5 py-1 text-xs font-medium text-[#0076CE]">
          Match #{rank}
        </span>
      </div>

      <p className="mt-4 text-sm leading-6 text-gray-300">{notes}</p>

      {explanation && (
        <div className="mt-5 rounded-2xl border-t border-gray-800 bg-gray-950/40 px-4 py-4">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Recommendation rationale
          </p>
          <p className="mt-2 text-sm leading-6 text-gray-300">
            {explanation}
          </p>
        </div>
      )}
    </div>
  );
}