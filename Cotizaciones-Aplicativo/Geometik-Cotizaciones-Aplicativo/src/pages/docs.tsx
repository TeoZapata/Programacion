import ComponenteCotizacion from "@/components/TablaCotizaciones";
import DefaultLayout from "@/layouts/default";

export default function IniciarCotizacionesPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <ComponenteCotizacion />
        </div>
      </section>
    </DefaultLayout>
  );
}
