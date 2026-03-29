
"use client";

import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

const serviceCategories = [
  {
    id: "full",
    label: "Full Detail",
    services: [
      {
        title: "Essential Detail",
        badge: "Popular",
        description: "A solid inside-and-out reset for daily drivers.",
        features: [
  "Interior vacuum",
  "Surface wipe-down",
  "Windows cleaned (in & out)",
  "Floor mats cleaned",
  "Hand wash & dry",
  "Wheels & tires cleaned",
  "Tire shine",
  "Quick paint protection"
],
        price: "$220",
      },
      {
        title: "Premium Detail",
        badge: "Recommended",
        description: "A more complete detail with deeper interior and exterior attention.",
        features:[
  "Everything in Essential",
  "Door jambs cleaned",
  "Deep wheel & tire cleaning",
  "Spot stain treatment",
  "Trim & plastics dressed",
  "Cargo area detailed",
  "Wax protection applied",
  "Enhanced interior detailing"
],
        price: "$295",
      },
      {
        title: "Showroom Detail",
        badge: "Best Value",
        description: "Our top full-detail package with added gloss and decontamination.",
        features: [
  "Everything in Premium",
  "Clay bar decontamination",
  "Multi-step paint correction",
  "High-gloss finish enhancement",
  "Leather conditioning",
  "Fabric protection treatment",
  "Final detail touch-up",
  "1-year paint sealant"
],
        price: "$375+",
      },
    ],
  },
  {
    id: "exterior",
    label: "Exterior Only",
    services: [
      {
        title: "Maintenance Wash",
        badge: "Essential",
        description: "Perfect for regular upkeep between deeper details.",
        features: ["Foam hand wash",
  "Microfiber dry",
  "Wheel face cleaning",
  "Tire shine",
  "Exterior windows cleaned",
  "Light bug removal",
  "Quick detail spray",
  "Clean finished look"
],
        price: "$85",
      },
      {
        title: "Exterior Detail",
        badge: "Popular",
        description: "A more complete exterior service focused on shine and protection.",
        features: [
  "Everything in Maintenance",
  "Bug & grime removal",
  "Door jamb cleaning",
  "Deep wheel cleaning",
  "Trim dressing",
  "Clay treatment",
  "Wax or sealant protection",
  "Improved gloss finish"
],
        price: "$140",
      },
      {
        title: "Paint Refresh",
        badge: "Premium",
        description: "For vehicles that need more than a wash and want added gloss.",
        features: [
  "Everything in Exterior Detail",
  "Full clay treatment",
  "Light paint correction",
  "Swirl & scratch reduction",
  "Enhanced gloss depth",
  "Paint smoothing treatment",
  "Premium finish protection",
  "Longer-lasting shine"
],
        price: "$225",
      },
    ],
  },
  {
    id: "interior",
    label: "Interior Only",
    services: [
      {
        title: "Interior Refresh",
        badge: "Essential",
        description: "A simple interior cleanup for a fresh daily-driver cabin.",
        features: [
  "Interior vacuum",
  "Surface wipe-down",
  "Windows & mirrors cleaned",
  "Floor mats cleaned",
  "Trash removal",
  "Dash & console cleaned",
  "Door panels wiped",
  "Quick interior reset"
],
        price: "$95",
      },
      {
        title: "Deep Interior",
        badge: "Popular",
        description: "A more complete interior reset with extra attention to buildup.",
        features: [
  "Everything in Refresh",
  "Spot stain treatment",
  "Cracks & crevices detailed",
  "Cup holders cleaned",
  "Dash & panels dressed",
  "Cargo area detailed",
  "Odor reduction treatment",
  "More detailed finish"
],
        price: "$165",
      },
      {
        title: "Seat & Carpet Reset",
        badge: "Deep Clean",
        description: "Best for dirtier interiors needing fabric and carpet attention.",
        features: [
  "Everything in Deep Interior",
  "Full seat shampoo",
  "Carpet shampoo extraction",
  "Deep stain removal",
  "Floor mat deep clean",
  "Fabric rejuvenation",
  "Heavy soil removal",
  "Interior restoration finish"
],
        price: "$240",
      },
    ],
  },
];
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const serviceOptions = [
  { value: "essential_detail", label: "Essential Detail", price: "220.00" },
  { value: "premium_detail", label: "Premium Detail", price: "295.00" },
  { value: "showroom_detail", label: "Showroom Detail", price: "375.00" },
  { value: "maintenance_wash", label: "Maintenance Wash", price: "85.00" },
  { value: "exterior_detail", label: "Exterior Detail", price: "140.00" },
  { value: "paint_refresh", label: "Paint Refresh", price: "225.00" },
  { value: "interior_refresh", label: "Interior Refresh", price: "95.00" },
  { value: "deep_interior", label: "Deep Interior", price: "165.00" },
  { value: "seat_carpet_reset", label: "Seat & Carpet Reset", price: "240.00" },
];
export default function Home() {
  const [activeCategory, setActiveCategory] = useState("full");
  const [headerCollapsed, setHeaderCollapsed] = useState(false);
    const [selectedService, setSelectedService] = useState("essential_detail");
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState("");
  const [availableSlots, setAvailableSlots] = useState<
    { value: string; label: string }[]
  >([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState("");
  const [bookingSuccess, setBookingSuccess] = useState("");
 const [detailLocation, setDetailLocation] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [vehicleMakeModel, setVehicleMakeModel] = useState("");
  const [notes, setNotes] = useState("");

  const selectedServiceData = useMemo(
    () => serviceOptions.find((service) => service.value === selectedService),
    [selectedService]
  );
useEffect(() => {
  const handleScroll = () => {
    setHeaderCollapsed(window.scrollY > 40);
  };

  handleScroll();
  window.addEventListener("scroll", handleScroll);

  return () => window.removeEventListener("scroll", handleScroll);
}, []);
useEffect(() => {
  if (!selectedDate) {
    setAvailableSlots([]);
    setSelectedSlot("");
    return;
  }

  const fetchSlots = async () => {
    try {
      setLoadingSlots(true);
      setBookingError("");
      setBookingSuccess("");
      setSelectedSlot("");

      const response = await fetch(
        `${API_BASE_URL}/api/bookings/available-slots/?date=${selectedDate}`
      );

      const data = await response.json();
console.log("slots response:", data);
      if (!response.ok) {
        throw new Error(data.error || "Failed to load available slots.");
      }

      setAvailableSlots(data.available_slots || []);

      if (data.is_bookable_day === false) {
        setBookingError(data.message || "This day is not available for booking.");
        return;
      }

      if ((data.available_slots || []).length === 0) {
        setBookingError(
          data.message || "No time slots are available for that date. Please choose another date."
        );
      }
    } catch (error: unknown) {
      setAvailableSlots([]);

      if (error instanceof Error) {
        setBookingError(error.message);
      } else {
        setBookingError("Could not load available slots.");
      }
    } finally {
      setLoadingSlots(false);
    }
  };

  fetchSlots();
}, [selectedDate]);

const handleBookingSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();

  setBookingError("");
  setBookingSuccess("");

  if (!selectedService) {
    setBookingError("Please choose a service.");
    return;
  }
if (!detailLocation.trim()) {
  setBookingError("Please enter the detail location.");
  return;
}
  if (!selectedDate) {
    setBookingError("Please choose a date.");
    return;
  }

  if (availableSlots.length === 0) {
    setBookingError("No time slots are available for that date. Please choose another date.");
    return;
  }

  if (!selectedSlot) {
    setBookingError("Please choose an available time slot.");
    return;
  }

  if (!customerName.trim()) {
    setBookingError("Please enter your name.");
    return;
  }

  if (!phone.trim()) {
    setBookingError("Please enter your phone number.");
    return;
  }
if (!email.trim()) {
  setBookingError("Please enter your email.");
  return;
}
  if (!vehicleMakeModel.trim()) {
    setBookingError("Please enter your vehicle make and model.");
    return;
  }

  try {
    setBookingLoading(true);

    const response = await fetch(`${API_BASE_URL}/api/bookings/create/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
  customer_name: customerName.trim(),
  phone: phone.trim(),
  email: email.trim(),
  vehicle_make_model: vehicleMakeModel.trim(),
  detail_location: detailLocation.trim(),
  notes: notes.trim() || "",
  service: selectedService,
  service_price: selectedServiceData?.price || "0.00",
  booking_date: selectedDate,
  time_slot: selectedSlot,
}),
    });

    const data = await response.json();
console.log("create booking response:", data);

if (!response.ok) {
  let message = "Booking failed.";

  if (typeof data?.error === "string") {
    message = data.error;
  } else if (Array.isArray(data?.error) && data.error.length > 0) {
    message = String(data.error[0]);
  } else if (data?.error && typeof data.error === "object") {
    const firstValue = Object.values(data.error)[0];
    if (Array.isArray(firstValue) && firstValue.length > 0) {
      message = String(firstValue[0]);
    } else if (typeof firstValue === "string") {
      message = firstValue;
    }
  } else if (data && typeof data === "object") {
    const firstValue = Object.values(data)[0];
    if (Array.isArray(firstValue) && firstValue.length > 0) {
      message = String(firstValue[0]);
    } else if (typeof firstValue === "string") {
      message = firstValue;
    }
  }

  throw new Error(message);
}

    setBookingSuccess("Booking submitted successfully.");
    setCustomerName("");
    setPhone("");
    setEmail("");
    setVehicleMakeModel("");
    setNotes("");
    setSelectedSlot("");
    setDetailLocation("");

    const refreshed = await fetch(
      `${API_BASE_URL}/api/bookings/available-slots/?date=${selectedDate}`
    );

    const refreshedData = await refreshed.json();
    setAvailableSlots(refreshedData.available_slots || []);
  } catch (error: unknown) {
    if (error instanceof Error) {
      setBookingError(error.message);
    } else {
      setBookingError("Something went wrong.");
    }
  } finally {
    setBookingLoading(false);
  }
};
  const activeServices =
    serviceCategories.find((category) => category.id === activeCategory)
      ?.services || [];

return (
  <main className="min-h-screen bg-white text-black">
    <div className="sticky top-0 z-[60]">
      <div
  className={`overflow-hidden bg-cyan-400 px-6 text-sm font-bold uppercase tracking-[0.18em] text-black transition-all duration-300 ${
    headerCollapsed
      ? "max-h-0 -translate-y-full opacity-0 py-0"
      : "max-h-20 translate-y-0 opacity-100 py-3"
  }`}
>
  <div className="flex items-center justify-center">
    50% Off For First-Time Customers
  </div>
</div>

      <header className="w-full border-b border-white/10 bg-black">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Image
              src="/white-logo.png"
              alt="High Desert Auto Detail logo"
              width={54}
              height={54}
              className="h-[54px] w-[54px] object-contain"
            />

            <div className="flex flex-col leading-none">
              <span className="text-2xl font-semibold uppercase tracking-[0.18em] text-white">
                High Desert
              </span>
              <span className="mt-1 text-sm font-medium uppercase tracking-[0.35em] text-cyan-400">
                Auto Detail
              </span>
            </div>
          </div>

          <nav className="hidden gap-8 text-sm font-medium md:flex">
            <a href="#" className="text-white transition hover:text-cyan-400">
              Home
            </a>
            <a href="#services" className="text-white transition hover:text-cyan-400">
              Services
            </a>
            <a href="#why-us" className="text-white transition hover:text-cyan-400">
              Why Us
            </a>
            <a href="#booking" className="text-white transition hover:text-cyan-400">
              Book
            </a>
          </nav>

          <div className="flex items-center gap-4">
            <a
              href="tel:5054016071"
              className="hidden items-center gap-2 text-sm font-medium text-white transition hover:text-cyan-400 md:flex"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
              >
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.86 19.86 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.86 19.86 0 0 1 2.08 4.18 2 2 0 0 1 4.06 2h3a2 2 0 0 1 2 1.72c.12.9.33 1.78.63 2.62a2 2 0 0 1-.45 2.11L8 9.91a16 16 0 0 0 6.09 6.09l1.46-1.24a2 2 0 0 1 2.11-.45c.84.3 1.72.51 2.62.63A2 2 0 0 1 22 16.92z" />
              </svg>
              <span>(505) 401-6071</span>
            </a>

            <a
              href="#booking"
              className="rounded-md bg-cyan-400 px-5 py-2 text-sm font-semibold text-black transition hover:bg-cyan-300"
            >
              Book Now
            </a>
          </div>
        </div>
      </header>
    </div>

    <section className="relative flex min-h-screen items-center justify-center px-6 pt-20">
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1607860108855-64acf2078ed9?auto=format&fit=crop&w=1600&q=80')] bg-cover bg-center opacity-55" />
      <div className="absolute inset-0 bg-black/35" />

      <div className="relative z-10 mx-auto flex max-w-5xl flex-col items-center text-center text-white">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">
          Mobile Auto Detailing in Albuquerque
        </p>

        <h1 className="max-w-4xl text-4xl font-bold leading-tight md:text-6xl">
          Premium Auto Detailing
          <br />
          At Your Home Or Office
        </h1>

        <p className="mt-6 max-w-2xl text-base text-gray-200 md:text-lg">
          Clean interiors. Glossy exteriors. Easy mobile service.
        </p>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row">
          <a
            href="#booking"
            className="rounded-md bg-cyan-400 px-8 py-4 font-semibold text-black transition hover:bg-cyan-300"
          >
            Book Online Now
          </a>
          <a
            href="#services"
            className="rounded-md border border-white px-8 py-4 font-semibold text-white transition hover:bg-white hover:text-black"
          >
            View Services
          </a>
        </div>
      </div>
    </section>

    <section
      id="services"
      className="scroll-mt-32 bg-white px-6 py-24 text-black"
    >
      <div className="mx-auto max-w-7xl">
        <h2 className="mb-4 text-center text-3xl font-bold md:text-5xl">
          Service Packages
        </h2>
        <p className="mx-auto mb-12 max-w-2xl text-center text-gray-600">
          Straightforward options for full, exterior-only, and interior-only detailing.
        </p>

        <div className="mx-auto mb-14 flex w-full max-w-2xl rounded-full border border-cyan-200 bg-white p-2 shadow-md">
          {serviceCategories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`flex-1 rounded-full px-4 py-3 text-sm font-semibold transition md:text-base ${
                activeCategory === category.id
                  ? "bg-black text-white shadow"
                  : "text-black hover:bg-zinc-100"
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>

        <div className="grid items-stretch gap-8 lg:grid-cols-3">
          {activeServices.map((service) => (
            <div
              key={service.title}
              className="flex h-full flex-col rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="mb-4 flex items-start justify-between gap-3">
                <h3 className="flex min-h-[72px] max-w-[70%] items-start text-3xl font-bold leading-tight">
                  {service.title}
                </h3>
                <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">
                  {service.badge}
                </span>
              </div>

              <div className="mb-5 text-3xl font-bold text-cyan-600">
                {service.price}
              </div>

              <p className="mb-8 min-h-[96px] text-lg leading-8 text-gray-700">
                {service.description}
              </p>

              <h4 className="mb-4 text-2xl font-bold">What’s Included</h4>

              <ul className="space-y-4 text-gray-800">
                {service.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <span className="mt-1 text-lg font-bold text-cyan-500">✓</span>
                    <span className="text-lg">{feature}</span>
                  </li>
                ))}
              </ul>

              <a
                href="#booking"
                className="mt-auto rounded-2xl bg-black px-6 py-4 text-center text-xl font-bold text-white transition hover:bg-zinc-800"
              >
                Book Now
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>

    <section id="why-us" className="bg-zinc-50 px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <h2 className="mb-12 text-center text-3xl font-bold md:text-4xl">
          Why Choose High Desert Auto Detail
        </h2>

        <div className="grid gap-8 md:grid-cols-3">
          <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm">
            <h3 className="text-xl font-bold text-cyan-600">Mobile Convenience</h3>
            <p className="mt-3 text-gray-700">
              We come to your home or office so your detail fits into your day.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm">
            <h3 className="text-xl font-bold text-cyan-600">Clean, Professional Results</h3>
            <p className="mt-3 text-gray-700">
              Proper products, careful technique, and a finish you can actually see.
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm">
            <h3 className="text-xl font-bold text-cyan-600">Simple Booking</h3>
            <p className="mt-3 text-gray-700">
              We’re building live scheduling so customers can pick open times online.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section id="booking" className="bg-white px-6 py-24">
      <div className="mx-auto max-w-5xl rounded-3xl border border-zinc-200 bg-zinc-50 p-8 shadow-sm md:p-10">
        <div className="mb-10 text-center">
          <h2 className="text-3xl font-bold md:text-4xl">Book Your Detail</h2>
          <p className="mt-3 text-gray-700">
            Choose your service, pick a date and time, and send us your booking request.
          </p>
        </div>

        <form onSubmit={handleBookingSubmit} className="grid gap-8">
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Service
              </label>
              <select
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
              >
                {serviceOptions.map((service) => (
                  <option key={service.value} value={service.value}>
                    {service.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Price
              </label>
              <div className="rounded-xl border border-zinc-300 bg-white px-4 py-3 text-lg font-bold text-cyan-600">
                ${selectedServiceData?.price ?? "0.00"}
              </div>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Date
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setSelectedSlot("");
                  setBookingError("");
                  setBookingSuccess("");
                }}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
              <p className="mt-2 text-sm text-gray-500">
                Pick a date to see available appointment times.
              </p>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Available Time Slots
              </label>

              {!selectedDate ? (
                <div className="rounded-2xl border border-dashed border-zinc-300 bg-white px-4 py-6 text-sm text-gray-500">
                  Select a date first to view available times.
                </div>
              ) : loadingSlots ? (
                <div className="rounded-2xl border border-zinc-200 bg-white px-4 py-6 text-sm text-gray-500">
                  Loading available time slots...
                </div>
              ) : availableSlots.length > 0 ? (
                <>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                    {availableSlots.map((slot) => {
                      const isSelected = selectedSlot === slot.value;

                      return (
                        <button
                          key={slot.value}
                          type="button"
                          onClick={() => {
                            setSelectedSlot(slot.value);
                            setBookingError("");
                          }}
                          className={`rounded-2xl border px-4 py-4 text-center text-sm font-semibold transition ${
                            isSelected
                              ? "border-cyan-500 bg-cyan-500 text-black shadow-md"
                              : "border-zinc-300 bg-white text-black hover:border-cyan-400 hover:shadow-sm"
                          }`}
                        >
                          <div className="text-base font-bold">{slot.label}</div>
                          <div className="mt-1 text-xs opacity-70">
                            {isSelected ? "Selected" : "Available"}
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {selectedSlot ? (
                    <p className="mt-3 text-sm font-medium text-cyan-700">
                      Selected time:{" "}
                      {availableSlots.find((slot) => slot.value === selectedSlot)?.label}
                    </p>
                  ) : (
                    <p className="mt-3 text-sm text-gray-500">
                      Choose one of the available time slots above.
                    </p>
                  )}
                </>
              ) : (
                <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-6 text-sm text-amber-800">
                  No appointments are available on this date. Please choose another date.
                </div>
              )}
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Name
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Phone
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Vehicle Make & Model
              </label>
              <input
                type="text"
                value={vehicleMakeModel}
                onChange={(e) => setVehicleMakeModel(e.target.value)}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Detail Location
              </label>
              <input
                type="text"
                value={detailLocation}
                onChange={(e) => setDetailLocation(e.target.value)}
                placeholder="Address, neighborhood, or business name"
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">
                Notes
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={5}
                className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-cyan-500"
              />
            </div>
          </div>

          {bookingError ? (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {bookingError}
            </div>
          ) : null}

          {bookingSuccess ? (
            <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm font-medium text-green-700">
              {bookingSuccess}
            </div>
          ) : null}

          <div className="text-center">
            <button
              type="submit"
              disabled={bookingLoading || !selectedDate || !selectedSlot}
              className="inline-flex rounded-xl bg-black px-8 py-4 text-lg font-bold text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {bookingLoading ? "Booking..." : "Book!"}
            </button>
          </div>
        </form>
      </div>
    </section>
  </main>
);
}