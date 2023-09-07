"""
Config file.

The unit used for time is second.
The unit used for distance is meter.
"""

from pathlib import Path

path = Path(__file__).parent.absolute()

OUTPUT_PREFIX = "" # "example_"
SEED_LIST = []
# SEED_LIST = [1,2,3,4,5,6,7,1687358010347487384]
NUMBER_OF_SIMULATIONS = 1
MAX_WORKERS = 4 # number of simultaneous processes

"""
First Solution Straegy Options:
'UNSET'
'AUTOMATIC'
'PATH_CHEAPEST_ARC'
'PATH_MOST_CONSTRAINED_ARC'
'EVALUATOR_STRATEGY'
'SAVINGS'
'SWEEP'
'CHRISTOFIDES'
'ALL_UNPERFORMED'
'BEST_INSERTION'
'PARALLEL_CHEAPEST_INSERTION'
'SEQUENTIAL_CHEAPEST_INSERTION'
'LOCAL_CHEAPEST_INSERTION'
'GLOBAL_CHEAPEST_ARC'
'LOCAL_CHEAPEST_ARC'
'FIRST_UNBOUND_MIN_VALUE'
"""
FIRSTSOLUTIONSTATEGY = 'PATH_CHEAPEST_ARC'

"""
Local Search Metaheuristic Options:
'UNSET', 'AUTOMATIC', 'GREEDY_DESCENT', 'GUIDED_LOCAL_SEARCH',
'SIMULATED_ANNEALING', 'TABU_SEARCH', 'GENERIC_TABU_SEARCH'
"""
LOCALSEARCHMETAHEURISTIC = 'GUIDED_LOCAL_SEARCH'
SOLUTION_LIMIT = 100 # number of solutions generated during the search
TIME_LIMIT = 1  # time limit in seconds

# used for TIME_WINDOWS, MAX_PATROLLING_TIME_PER_VEHICLE
# and TIME_OF_EVENT_MAX
# does end the simulation implicitly:
# - there are no more emergencies after that time
# - time windows for patrol locations end at that time
SIMULATION_DURATION = 60*60*3

# the police station can not be a patrol_locations
# patrol locations need to be different as index_to_osm needs to be bijective
PATROL_LOCATIONS = [294231718, 2261966238, 61832440, 59640989, 127376799,
                    83699821, 553281114, 4735664742, 321396211, 60215025,
                    62592634, 293281751, 84287724, 36491424, 61838230,
                    78431380, 2309659180, 98806881, 60214963, 123701586,
                    61837807, 27027753, 61831060, 17322884, 293190866,
                    5897096465, 59640976, 1844621714, 103664213, 127367892]

TIME_WINDOWS = [(0, SIMULATION_DURATION) for _ in PATROL_LOCATIONS]

NUMBER_OF_VEHICLES = 4
PATROLLING_TIME_PER_LOCATION = 60*5

# is used in each calculation and never updated
# therefore it only guarantees that the initial routes without
# emergencies finish in time
MAX_PATROLLING_TIME_PER_VEHICLE = SIMULATION_DURATION  # 86400 for one full day

# real police stations in favoriten
# [7057695920, 103661672, 250119553, 92411700, 60569895, 984865145, 6418881190]
POLICE_STATION = 60569895

# needs to be NUMBER_OF_VEHICLES long
STARTS = [POLICE_STATION for _ in range(NUMBER_OF_VEHICLES)]

# patrolling ends at the police station
# ends = [POLICE_STATION for i in range(NUMBER_OF_VEHICLES)] # happens in create_data_model

NUMBER_OF_EVENTS_MU = 6
NUMBER_OF_EVENTS_SIGMA = 4
TIME_OF_EVENT_MIN = 0
TIME_OF_EVENT_MAX = SIMULATION_DURATION
EVENT_MIN_DURATION = 60*2
EVENT_DURATION_MU = 60*15
EVENT_DURATION_SIGMA = 60*5

# possible event locations
# all locations except the police station
POSSIBLE_LOCATIONS_OF_EVENTS = [17322879, 17322882, 17322883, 17322887, 17322888, 17322889, 17322896, 17322899, 27027753, 27027755, 27027758, 27027786, 27027934, 27027935, 27027938, 27027939, 27027940, 27377265, 27377267, 27377268, 29006387, 29006395, 29006403, 29006408, 29006423, 29006424, 29006426, 29006430, 29006478, 29006482, 33382004, 33382008, 33382020, 33382021, 34516819, 34516826, 34588177, 36491421, 36491424, 36491486, 36621812, 36621814, 36621815, 36621817, 36621818, 53169050, 53169052, 53171130, 53171131, 53171136, 53171137, 53171518, 53171938, 53171939, 53171941, 53171942, 53171944, 53171945, 53171948, 53171949, 53172313, 53172315, 53172458, 53172459, 53172460, 59640969, 59640971, 59640975, 59640976, 59640977, 59640981, 59640989, 59641373, 59641374, 59641378, 59641379, 59641391, 59641392, 59641398, 59641399, 59641400, 59641401, 59641413, 59641414, 59641417, 59641421, 60214685, 60214747, 60214839, 60214840, 60214841, 60214867, 60214963, 60214964, 60214965, 60214966, 60214967, 60214968, 60214969, 60214970, 60214971, 60214972, 60215021, 60215022, 60215023, 60215024, 60215025, 60215026, 60215027, 60215043, 60215069, 60215071, 60215080, 60215082, 60215087, 60215089, 60215092, 60215096, 60215097, 60215116, 60215174, 60215175, 60215176, 60215177, 60215178, 60215179, 60215180, 60569894, 60569895, 60569896, 60569901, 60569912, 60569914, 60569915, 60569916, 60569918, 60569919, 60569923, 60584125, 60584131, 60584137, 60584143, 60584144, 60584155, 60584156, 60584168, 60584169, 60739029, 60739393, 60827802, 61768694, 61830896, 61830898, 61830899, 61830900, 61830901, 61831060, 61831061, 61831213, 61831214, 61831215, 61831391, 61831432, 61831449, 61831617, 61831730, 61831769, 61831808, 61831813, 61831867, 61831870, 61832001, 61832002, 61832004, 61832005, 61832006, 61832007, 61832010, 61832055, 61832056, 61832058, 61832059, 61832061, 61832067, 61832219, 61832279, 61832281, 61832282, 61832283, 61832347, 61832348, 61832350, 61832437, 61832439, 61832440, 61832441, 61832921, 61832923, 61832924, 61832927, 61832928, 61832931, 61832935, 61832936, 61832938, 61832943, 61832953, 61833992, 61833995, 61833997, 61833999, 61834193, 61834197, 61834198, 61834200, 61834204, 61834362, 61834365, 61834698, 61834704, 61834708, 61834713, 61835218, 61835229, 61835238, 61835239, 61835877, 61835879, 61835880, 61835881, 61836666, 61836724, 61837803, 61837807, 61838220, 61838224, 61838230, 61838558, 61838559, 61838560, 61838869, 61838871, 61838877, 61838878, 61838880, 61851283, 62592209, 62592357, 62592633, 62592634, 62592743, 62593275, 62593276, 62593278, 62593279, 62593505, 62593506, 62593507, 62593508, 62593893, 62593894, 62593896, 62593997, 62594344, 62594610, 62594611, 62594613, 62594614, 62594842, 62594844, 62594845, 62594848, 62594851, 62595127, 62595130, 62595548, 62595549, 62595552, 62595827, 62595828, 62595829, 62595831, 62596460, 62596463, 62596465, 62596468, 62596470, 62596471, 62596473, 62596484, 62596487, 62597125, 62597127, 62597361, 62597362, 62597365, 62597369, 62598139, 62598141, 62598523, 62598716, 65098055, 65098828, 65098833, 65098841, 65099680, 65099681, 65099682, 65099684, 65099685, 78431380, 78431381, 78431390, 83694717, 83694864, 83697945, 83699814, 83699815, 83699818, 83699820, 83699821, 83699822, 83699824, 83699826, 83699829, 83699830, 83699844, 83701341, 83701343, 83701344, 84285756, 84285900, 84285911, 84286158, 84286171, 84286202, 84286766, 84286798, 84286882, 84286927, 84286931, 84287010, 84287012, 84287086, 84287094, 84287227, 84287291, 84287711, 84287712, 84287716, 84287718, 84287719, 84287724, 84287837, 84771434, 84771453, 84771461, 84771465, 84771478, 84771487, 84772812, 84772815, 84772817, 84772820, 84773198, 84773199, 84773200, 84773317, 84773319, 84773911, 84773915, 84773916, 86002346, 86002348, 88197189, 88197191, 88197507, 88197514, 88197782, 88198733, 88198735, 88198798, 88198800, 88199035, 88199117, 88199153, 88199425, 88199919, 88199923, 88200215, 88200222, 88203315, 88203322, 88203324, 88203326, 88204044, 88204053, 90019977, 90019978, 90019979, 90020320, 90020321, 90020653, 90020657, 90021107, 90021109, 90021305, 90175494, 92410633, 92410637, 92410727, 92410977, 92410978, 92411387, 92411388, 92411454, 92411455, 92411596, 92411598, 92411599, 92411600, 92411602, 92411604, 92411700, 92411702, 93422891, 93423081, 93423082, 93423083, 93423085, 93423565, 93423773, 93423774, 93423867, 93423907, 93424089, 93424151, 93424313, 93424314, 93424683, 93424753, 93424870, 93424871, 93424874, 93425381, 93425387, 93425391, 93425493, 93425494, 98413091, 98414320, 98419920, 98693581, 98806460, 98806461, 98806463, 98806464, 98806466, 98806881, 103655613, 103655898, 103656034, 103656317, 103656325, 103656328, 103657481, 103657482, 103657556, 103657800, 103657807, 103658692, 103658693, 103658708, 103658711, 103658717, 103659103, 103659105, 103659516, 103659519, 103659528, 103659678, 103660632, 103660638, 103660643, 103660646, 103660652, 103660655, 103660659, 103661669, 103661672, 103664211, 103664213, 103664216, 103664217, 103667836, 108227637, 108227644, 108227648, 108227651, 108229263, 108230093, 108230102, 108230121, 108230125, 108230634, 108230635, 108230637, 108231000, 108231001, 108231549, 108231551, 108231552, 108231988, 108231989, 108232516, 108232517, 108232523, 108233359, 108233610, 108233612, 108233615, 108234272, 108234276, 108234837, 108234840, 108235159, 108235201, 110329582, 110331745, 110331747, 110331751, 110331756, 122752282, 122752310, 122752369, 122752386, 122752405, 123275230, 123678748, 123682053, 123682778, 123682780, 123682783, 123682806, 123683389, 123683397, 123683820, 123683950, 123684429, 123684864, 123684866, 123684889, 123693361, 123693363, 123694322, 123696561, 123699429, 123701517, 123701521, 123701528, 123701529, 123701533, 123701534, 123701536, 123701537, 123701542, 123701561, 123701564, 123701569, 123701574, 123701577, 123701580, 123701581, 123701586, 123704797, 123737880, 123737884, 123743212, 123746798, 123749340, 123750161, 123752235, 123752475, 123752836, 123752839, 123752848, 123754125, 123754224, 123755712, 127353661, 127353666, 127354027, 127354275, 127364708, 127364721, 127364982, 127365254, 127365889, 127366513, 127366523, 127366777, 127366780, 127366961, 127366963, 127367081, 127367084, 127367508, 127367713, 127367719, 127367882, 127367888, 127367892, 127368106, 127368285, 127368690, 127368691, 127368928, 127368930, 127369316, 127369317, 127369319, 127369320, 127369768, 127371705, 127372084, 127372088, 127372239, 127372240, 127372836, 127372839, 127372842, 127372849, 127373236, 127373704, 127374433, 127375807, 127375825, 127375827, 127375828, 127376291, 127376799, 127376801, 127376805, 127376807, 127377112, 127377114, 127377392, 127377693, 127377697, 127377699, 127377984, 127379422, 127379423, 127379428, 127379442, 127379452, 127379453, 127379931, 129543321, 129545467, 129545470, 129545471, 129545472, 129942036, 129942047, 129942050, 129942063, 129942064, 129942160, 129942163, 129942170, 129942176, 129942187, 129942188, 129942189, 130232678, 130232679, 130232699, 130232768, 130232810, 130232811, 130232823, 130232836, 130233888, 130233897, 130233899, 132251552, 134726724, 139374234, 139374237, 139376964, 139377809, 139378255, 140452739, 140452972, 144608149, 144608561, 194647466, 194647508, 194647534, 194647555, 194647651, 194647665, 207270619, 207271311, 207388912, 207389090, 207389139, 213440856, 213440860, 213440869, 213440878, 213440912, 213449046, 213451282, 213451284, 213456004, 213456009, 223659199, 223659307, 223660235, 223660241, 223661216, 223662445, 223662584, 223662674, 223663836, 223663840, 223664015, 223664712, 223664714, 223668357, 223668359, 229503395, 229503720, 229505190, 229506568, 229507174, 229507175, 229507301, 229507303, 244137754, 244137884, 244137885, 244137886, 250119247, 250119282, 250119494, 250119553, 252274397, 252274469, 252278444, 252278546, 252279998, 252281124, 252281389, 252281392, 252281626, 252616472, 252616473, 252616582, 252616587, 253438091, 253438096, 253438100, 253438105, 257157413, 257754901, 267149938, 267149939, 286409445, 287747741, 287747829, 287747851, 287748976, 287748984, 287749074, 287749397, 291864105, 292049636, 292379001, 292399865, 292399869, 292399870, 293186400, 293186405, 293188582, 293190609, 293190610, 293190837, 293190838, 293190866, 293190981, 293192757, 293192760, 293194746, 293194747, 293194750, 293194997, 293195032, 293195033, 293197593, 293200723, 293201161, 293201275, 293201284, 293201581, 293201601, 293279861, 293279980, 293281751, 293281781, 293282431, 293284712, 293287930, 293800956, 293802324, 294042577, 294231718, 294232256, 294232607, 294232661, 294233530, 294235850, 294239171, 295405726, 295405766, 295413026, 295414216, 295414234, 295414245, 295415101, 295417064, 295422941, 295431612, 295438773, 296029947, 296030087, 296031598, 296031599, 296033364, 296033476, 296033702, 296034711, 297771109, 298161859, 298161861, 298161869, 298161872, 298161874, 298161907, 298595411, 298595424, 298611846, 298611850, 298613176, 298728318, 298735700, 298735704, 298735706, 298735710, 299084684, 299085688, 301695114, 301695121, 301697842, 301697843, 301698732, 301698950, 301699032, 301699689, 301699756, 301922580, 301922603, 301922973, 301924603, 301924775, 301924941, 301926209, 301926248, 301927166, 301927436, 301931849, 301933391, 302771387, 302771409, 302771444, 302771445, 302771671, 302771691, 302771692, 302771711, 302771782, 302772208, 302772216, 302772274, 302772277, 303011220, 303011643, 303011785, 303012076, 303012343, 303016205, 303016810, 304026147, 304026181, 304036955, 304043948, 304303225, 304354906, 305152603, 305189890, 305195064, 305196046, 305630209, 305630225, 305638480, 305640831, 305643490, 305726869, 306224178, 306224179, 306224290, 306224291, 306224358, 306225554, 306229608, 306230876, 306257733, 306257964, 308742524, 308742525, 308742528, 312158566, 312160885, 315529283, 315529371, 315529372, 315530539, 315532303, 315532304, 317375629, 317405975, 320243980, 321391275, 321391997, 321392865, 321393864, 321394489, 321394547, 321394984, 321396210, 321396211, 321681644, 321681923, 321683097, 321685456, 321685473, 321688077, 321690725, 321692775, 321709181, 321709184, 321709238, 321709253, 321709263, 321709272, 321709273, 321709499, 321709620, 321709710, 321709711, 321709758, 321710596, 321711024, 321711035, 321711036, 321711037, 321775232, 321776589, 321778292, 321785758, 321786161, 321786177, 321787532, 321921842, 321921883, 321925490, 321925588, 321925969, 331040139, 331040142, 335882807, 335882820, 335886722, 336410734, 336410742, 360356022, 418803625, 418803626, 458100726, 458410248, 461613704, 506487851, 509292529, 553281114, 553281130, 553281132, 560530785, 582563639, 582563641, 588436517, 597465575, 602223823, 706464962, 790655462, 795006523, 795148481, 809927233, 810356770, 810356781, 898668297, 923566894, 984864377, 984865145, 985851618, 996669061, 1086176329, 1086176383, 1086176387, 1086176388, 1086176430, 1092776750, 1092817457, 1092817469, 1092817472, 1092817474, 1112976283, 1161883710, 1162347719, 1165878659, 1314636923, 1377839736, 1379910932, 1379910937, 1387509198, 1387509200, 1445703697, 1445735725, 1515389023, 1544762818, 1595551513, 1595551514, 1597347044, 1611012983, 1623833792, 1643999873, 1651546653, 1670015240, 1714031655, 1742570120, 1742570121, 1750260311, 1773288747, 1788569527, 1829857666, 1829857678, 1829857679, 1829857697, 1829862481, 1829890434, 1830094303, 1832054951, 1839834870, 1839834871, 1839834872, 1839840819, 1844598964, 1844621711, 1844621713, 1844621714, 1844621716, 1857414924, 1956787116, 1956787118, 1956787120, 1956787130, 1956787132, 1958117352, 1985704054, 2002522963, 2053297137, 2060841206, 2060842439, 2061414510, 2106209116, 2157156993, 2200457973, 2200457980, 2218132374, 2231397323, 2260653595, 2261966210, 2261966229, 2261966232, 2261966238, 2261966240, 2309659095, 2309659180, 2352878291, 2447519816, 2456883586, 2526546837, 2619113674, 2681486470, 2695119656, 2695119698, 2695140333, 2695140337, 2705177625, 2705177672, 2717493579, 2717493644, 2781963266, 2781963329, 2781971144, 2781971146, 2781971164, 2879522601, 3069890606, 3147454365, 3147454366, 3188901149, 3216199497, 3249726527, 3249726549, 3251659367, 3262508375, 3262508389, 3310548246, 3310548253, 3310548254, 3379808080, 3482712904, 3511736260, 3534479755, 3534479782, 3534558946, 3556279959, 3561176615, 3561176616, 3595058139, 3595058140, 3613479696, 3621599903, 3621599905, 3632371690, 3674544936, 3762419778, 3805169170, 3805169175, 3805169180, 3805169181, 3805169185, 3835886946, 3835886950, 3835890960, 3867675622, 4278115340, 4371634604, 4371634622, 4371634626, 4540208237, 4546907672, 4546907680, 4571749924, 4593210496, 4635311622, 4724214298, 4724214313, 4724251330, 4724251353, 4724257134, 4724257145, 4724257148, 4724257154, 4724257160, 4724257165, 4735664741, 4735664742, 4794040364, 4806499498, 4846035324, 4885697234, 4895735225, 5015873914, 5018221333, 5020815479, 5218737607, 5241577887, 5314200657, 5314200658, 5314200663, 5314200674, 5314200676, 5488956548, 5513574198, 5552794696, 5552794697, 5552794698, 5816163368, 5821322486, 5827060324, 5827060328, 5827060329, 5827060337, 5841658443, 5841674747, 5895107889, 5895107890, 5897096465, 6056294402, 6138183434, 6418881190, 6418881201, 6739847853, 6739847856, 6739847859, 6739898998, 6739899001, 6810319860, 6810319865, 6810405629, 6810405634, 6810405639, 6853942832, 7019533573, 7057695920, 7106735436, 7106735442, 7261690073, 8165434227, 8681352265, 17322884]



if POLICE_STATION in PATROL_LOCATIONS:
    raise ValueError('POLICE_STATION cannot be in PATROL_LOCATIONS')


if __name__ == '__main__':
    print("please do not run as main")
