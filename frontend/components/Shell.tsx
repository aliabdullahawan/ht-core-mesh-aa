"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { clearSession, getSession, homeFor, Role, SessionUser } from "@/lib/api";

const LINKS: { href: string; label: string; roles: Role[] }[] = [
  { href: "/projects", label: "Projects", roles: ["ADMIN", "MANAGER", "AGENT"] },
  { href: "/transcript", label: "Create from Transcript", roles: ["ADMIN"] },
  { href: "/my-tasks", label: "My Tasks", roles: ["AGENT"] },
  { href: "/team", label: "Team", roles: ["ADMIN", "MANAGER", "AGENT"] },
];

/** Route guard + top bar. `roles` hides the page from other roles (the backend enforces it too). */
export default function Shell(props: { children: React.ReactNode; roles?: Role[] }) {
  // URL hooks (usePathname/useParams) must sit inside Suspense in Next 16
  return (
    <Suspense fallback={null}>
      <ShellInner {...props} />
    </Suspense>
  );
}

function ShellInner({ children, roles }: { children: React.ReactNode; roles?: Role[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<SessionUser | null>(null);
  const allowed = roles?.join(",");

  useEffect(() => {
    const u = getSession();
    if (!u) return router.replace("/login");
    if (allowed && !allowed.split(",").includes(u.role)) return router.replace(homeFor(u.role));
    // Session lives in localStorage, which only exists after mount
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setUser(u);
  }, [router, allowed]);

  if (!user) return null;

  function logout() {
    clearSession();
    router.replace("/login");
  }

  return (
    <>
      <header className="topbar">
        <span className="brand">NovaWorks PM</span>
        <nav className="nav">
          {LINKS.filter((l) => l.roles.includes(user.role)).map((l) => (
            <Link key={l.href} href={l.href} className={pathname.startsWith(l.href) ? "active" : ""}>
              {l.label}
            </Link>
          ))}
        </nav>
        <span className="who">
          {user.name} · {user.role.toLowerCase()}
        </span>
        <button className="btn secondary" onClick={logout}>
          Logout
        </button>
      </header>
      <main className="page">{children}</main>
    </>
  );
}
