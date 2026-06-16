export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white">

      {/* Navbar */}
      <nav className="flex justify-between items-center p-8">

        <h1 className="text-2xl font-bold tracking-wide">
          SOPHIA
        </h1>

        <div className="space-x-6 text-gray-400">
          <a href="/dashboard">
            Dashboard
          </a>

          <a href="/login">
            Login
          </a>
        </div>

      </nav>


      {/* Hero */}

      <section className="flex flex-col items-center justify-center mt-32">


        <h2 className="text-6xl font-bold text-center">

          See the intelligence
          <br />

          behind wallets

        </h2>


        <p className="mt-6 text-gray-400 text-lg max-w-xl text-center">

          Track wallets.
          Analyze behavior.
          Discover smart money.

          Sophia turns blockchain data into actionable intelligence.

        </p>


        <a
          href="/dashboard"
          className="
          mt-10
          px-8 py-4
          rounded-xl
          bg-white
          text-black
          font-semibold
          hover:opacity-80
          "
        >
          Enter Sophia
        </a>


      </section>



      {/* Feature cards */}

      <section className="grid md:grid-cols-3 gap-6 p-10 mt-32">


        <Card
          title="Wallet Tracking"
          text="Monitor wallets and detect movements in real time."
        />

        <Card
          title="Behavior Analysis"
          text="Understand trading patterns and wallet history."
        />

        <Card
          title="Smart Money"
          text="Identify profitable wallets before they move."
        />


      </section>


    </main>
  );
}



function Card(
 {
  title,
  text
 }: {
  title:string,
  text:string
 }
){

return (

<div
className="
border
border-gray-800
rounded-2xl
p-6
bg-gray-950
"
>

<h3 className="text-xl font-bold">
{title}
</h3>


<p className="text-gray-400 mt-3">
{text}
</p>


</div>

)

}