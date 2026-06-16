import Link from "next/link";


export default function Sidebar() {

return (

<div
className="
fixed
left-0
top-0
h-screen
w-64
bg-gray-950
border-r
border-gray-800
p-6
text-white
"
>


<h1 className="
text-2xl
font-bold
mb-10
tracking-wider
">
SOPHIA
</h1>



<nav className="space-y-3">


<Menu
name="Dashboard"
href="/dashboard"
/>


<Menu
name="Wallet Intelligence"
href="/wallets"
/>


<Menu
name="Token Scanner"
href="/tokens"
/>


<Menu
name="Smart Money"
href="/smart-money"
/>


<Menu
name="Alerts"
href="/alerts"
/>


<Menu
name="Watchlist"
href="/watchlist"
/>


<Menu
name="Settings"
href="/settings"
/>

<Menu
name="Token Traders"
href="/traders"
/>



</nav>



</div>

)

}



function Menu(
{
name,
href
}:{
name:string,
href:string
}
){

return (

<Link

href={href}

className="
block
p-3
rounded-lg
text-gray-400
hover:bg-gray-900
hover:text-white
transition
"

>

{name}

</Link>

)

}