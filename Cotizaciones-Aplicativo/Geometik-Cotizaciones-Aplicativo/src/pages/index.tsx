import { Link } from "@nextui-org/link";
import { button as buttonStyles } from "@nextui-org/theme";

import { siteConfig } from "@/config/site";
import DefaultLayout from "@/layouts/default";
import { Image } from "@nextui-org/image";

export default function InicioPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="flex gap-3">
          <Link
            isExternal
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
            })}
            href={siteConfig.links.docs}
          >
            Lucy CHEC - Copia Factura
            <Image src="./images/lucy.jpg" />
          </Link>
        </div>
      </section>
    </DefaultLayout>
  );
}
