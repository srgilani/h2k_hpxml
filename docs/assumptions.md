## Assumptions
- Attic/gable ceilings are assumed to not have gable walls defined in the h2k file. They are created in the translation process by assuming conventional rectangular geometry, where half the "length" ceiling input is assumed to be one side of the rectangle.
- All attics are assumed to be vented
- Area of gable ends of cathedral ceilings are assumed to have been defined within h2k wall components.
- Attic/Hip type ceilings assume that the "length" input provided is the ceiling perimeter (all edges are compressed)
- Scissor ceiling surfaces are assumed to be at half the pitch of the roof (i.e. if a roof slope is 4/12, ceiling surface slope is 2/12)
- HPXML's default occupant and appliance schedules are used.
- Split level and split entry options in HOT2000 are treated as 2 storeys when counting the number of conditioned floors in HPXML.
- The HPXML workflow states that enclosed spaces such as garages should be explicitly included in the model. However, HOT2000 files do not account for these spaces, so they are ignored in the translation process.

- The "Adjacent to unconditioned space" checkbox in HOT2000 is assumed to be equivalent to "other non-freezing space" for attached buildings, and but there is no allowable HPXML equivalent for detached buildings. Therefore, we must use "outside" for buffered wall exteriors for detached buildings unless we model the entire garage or there is another HPXML workaround


- Windows can only be attached to wall components in HPXML, not doors. The current solution is to attach windows on doors to the parent wall of the door, and subtract the window area from the door area.
- For basement walls, the AssemblyEffectiveRValue includes the concrete or wood wall portion.
- Pony wall area is calculated as `pony wall height` * `exposed basement perimeter`.
- Above slab insulation is mapped to below slab insulation in HPXML, which has no above slab option.
- For slab perimeter insulation (UnderSlabInsulation), we include any under-footing measurement in the width provided to HPXML, if applicable.
- Carpet fraction and R-value for slabs overwritten with 0, otherwise HPXML defaults to values >0.
- Standard operating conditions are hard coded for base loads.
- Appliance Energy Guide Label inputs have been reverse engineered to achieve appliance water and energy consumption results that match HOT2000's standard operating conditions.
- All "exterior use" consumption in HOT2000's baseloads are lumped under exterior lighting in HPXML.


### Field Assumptions:
- Building Site Type = suburban
- Building Site Surroundings = stand-alone
