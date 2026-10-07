"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { getSession, homeFor } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const u = getSession();
    router.replace(u ? homeFor(u.role) : "/login");
  }, [router]);
  return null;
}
