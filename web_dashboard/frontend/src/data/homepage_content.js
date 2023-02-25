import React from 'react';
import { A } from 'hookrouter';
import { BLOB_STORAGE_URL } from './constants';
import CleanEnergyBarLegend from '../components/graphs/miscLegends/CleanEnergyBarLegend/CleanEnergyBarLegend';
import InterconnectionMapLegend from '../components/graphs/BranchMap/InterconnectionMapLegend';
import UpgradedInterconnectionMapLegend from '../components/graphs/miscLegends/UpgradedInterconnectionMapLegend/UpgradedInterconnectionMapLegend';

const HOMEPAGE_IMAGES_URL = BLOB_STORAGE_URL + '/homepage/';

const gridIntroText = (
  <>
    <p>The U.S. electric grid is the system that moves energy from power sources like wind farms, solar panels, and nuclear plants to the homes and other buildings where that power is used. It is arguably the most complicated machine in the world, encompassing three separate grids—Eastern, Western, and Texas—and connecting 7,000 power plants via 300,000 miles of high-voltage transmission lines, which then connect to millions of miles of distribution lines that bring power into our homes, workplaces, and schools.</p>
    <p>What is the most efficient and cost-effective way to transform such a complex, continent-spanning network? Leaders across the country will be making important decisions over the next few years about how to modernize the grid and help the country reach our climate goals, so we built a sophisticated, open-source model of the U.S. energy system to give them the tools to make the right choices. Frequently, high resolution models like ours are proprietary and expensive to access – that makes it hard for decision-makers around the U.S. to check each other’s assumptions and puts these tools out of reach to university researchers on a more limited budget. Since we created the grid model using only publicly available information, anyone can freely use and distribute the data it generates.</p>
  </>
);

const gridText = (
  <>
    <p>The map above shows the transmission network in our model. Each line represents a high-voltage transmission line. The thick pink lines represent High Voltage Direct Current (HVDC) lines: transmission lines capable of efficiently transporting electricity over long distances, and the dotted lines show where our three regional grids are separated.</p>
    <p>Using hourly estimates of both the demand for electricity and the generation potential from wind, solar, and hydro resources, our grid model can simulate what will happen when we implement clean energy policies and technologies. These simulations show that a cleaner and brighter future is possible—if we invest now in the clean energy infrastructure that will make it happen.</p>
  </>
);

const capacityText = (
  <>
    <p>Thanks to technological advances and policy incentives, the costs of clean renewable-energy sources continue to come down—but we still need to add more clean energy to the grid to accommodate all the sectors of the economy, such as manufacturing and transportation, that will be more electrified in the future.</p>
    <p>This figure shows how much clean energy we need to add to reach net-zero emissions. We will need a mix of firm resources, like nuclear, geothermal and hydroelectric, as well as variable resources, like wind and solar. Variable resources are cheaper but are not as consistent as firm resources. A mix of the two types of clean energy (along with grid-scale battery storage) will give us the power we need, while also providing a reliable and resilient grid.</p>
    <p>Our model can help experts and lawmakers determine the best mix of clean energy types and where to add them to the grid.</p>
  </>
);

const hvdcLink = <A href="/key-findings/macro-grid">here</A>

const hvdcText = (
  <>
    <p>Adding more clean energy is just the first step. Renewable sources like wind and solar sometimes produce more energy than can be used in a given place at a given moment, and this energy is wasted if it can’t be moved to somewhere it is needed or stored for later use. (This problem is called curtailment.) Energy is also wasted if there is too much congestion in transmission lines. Like roads, once the lines are gridlocked, no more energy can get through.</p>
    <p>Right now, the US electric grid is actually three separate grids. Adding all the renewable power we need will create more curtailment and congestion, so we also need more transmission capacity to move this energy and better knit our nation’s three grids together. One way to do that is to create a wide-ranging nationwide HVDC network to connect the seams across the three grids. More details can be found {hvdcLink}.</p>
    <p>Along with the HVDC network, we’ll need to further upgrade transmission within the three grids. Using our model, policymakers can see and simulate where energy is currently being wasted and determine the best places to add transmission lines to reduce waste, curtailment, and congestion and put more clean energy to work across the country.</p>
  </>
);

const transmissionText = (
  <p>Connecting America’s three separate grids means that we can unlock America’s abundant geographic clean energy diversity.  This means moving energy from the windiest and sunniest parts of the country to exactly where it’s needed, when it’s needed. This is critical to integrating more clean energy onto the grid and making the most of America’s clean energy resources. By unlocking geographic diversity in clean energy we can build a clean grid with less investment than we’d need if each state or even each region attempted to add clean energy on their own.</p>
);

const storageText = (
  <>
    <p>One reason the power grid is so complex is because, at every instant, it must balance supply and demand. Transmission upgrades can help by moving electricity efficiently from place to place. But what if, instead of this constant balancing act, the grid was connected to batteries that could store the extra energy generated when the wind blows and the sun shines and release it when the wind is calm and the sky is dark? Greater storage capacity will allow power to be kept in reserve when it’s not needed and used when it is.</p>
    <p>As costs come down and new technologies come online, energy storage will become an increasingly attractive solution. But, as the figure above shows, to reach net-zero emissions by 2050, we will need to add much, much more storage to the grid.</p>
    <p>We're building tools to determine how much storage we need, and also what types of storage are optimal and where to locate them. Storage duration is a big question as well – we need everything from short-term storage to smooth out daily supplies, seasonal storage to account for unusual long-term weather patterns, and a mix of storage types in between. To reach net-zero emissions by 2050, we need a national roadmap for modernizing the U.S. electricity system in the next two years. To help design this roadmap, in the coming months we at BE Sciences will delve into the best solutions for improving grid-wide storage capacity.</p>
  </>
);

/* TODO: graph and mobile graph is a KLUDGEY solution. We should pass the URL instead! */
export const GRID_INFO = {
  grid: {
    title: 'Our Model of the Electric Grid',
    graphTitle: 'The Transmission Network',
    introText: gridIntroText,
    graphImageUrl: HOMEPAGE_IMAGES_URL + 'Transmission_Grid_Current.png',
    legend: <InterconnectionMapLegend />,
    text: gridText
  }
};

export const ACCORDION_INFO = {
  capacity: {
    title: 'Adding Clean Energy',
    text: capacityText,
    graphCaption: 'Clean Energy Mix Today and in the Future',
    graphs: [{
      graphTitle: null,
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'CleanEnergyBarChart.png',
      graphText: null,
      legend: <CleanEnergyBarLegend />,
    }],
  },
  hvdc: {
    title: 'Investing in Transmission',
    text: hvdcText,
    graphCaption: 'Stitching Together the Existing Grids to Eliminate Congestion',
    graphs: [{
      graphTitle: 'The Grid Today',
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'Transmission_Grid_Current.png',
      graphText: <p>If we dramatically increase renewables without connecting our regional grids, we’ll end up wasting money and energy.</p>,
      legend: <InterconnectionMapLegend />
    }, {
      graphTitle: 'Connected Grid',
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'Transmission_Grid_Upgraded.png',
      graphText: <p>This figure shows what an effective HVDC network would look like for connecting the three separate interconnections (grids).</p>,
      legend: <UpgradedInterconnectionMapLegend />
    }]
  },
  transmission: {
    title: 'Unlocking Geographic Diversity',
    text: transmissionText,
    graphCaption: 'A Model to Move Renewable Energy to where it\'s Needed',
    graphs: [{
      graphTitle: 'Morning',
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'GeographicDiversity_Morning.png',
      graphText: <p>In the early morning, excess wind and solar capacity in the Midwest and the South feed the West Coast, where the sun hasn't risen yet.</p>,
      legend: null,
    }, {
      graphTitle: 'Afternoon',
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'GeographicDiversity_Afternoon.png',
      graphText: <p>As the East Coast reaches peak usage around 2-5pm ET, excess solar and wind energy flows eastward from the West Coast and Texas.</p>,
      legend: null,
    }]
  },
  storage: {
    title: 'Adding Storage',
    text: storageText,
    graphCaption: 'Current Storage VS. Total Needed by 2050',
    graphs: [{
      graphTitle: null,
      graphImageUrl: HOMEPAGE_IMAGES_URL + 'BatteryStorage.png',
      graphText: null,
      legend: null,
    }]
  },
};
