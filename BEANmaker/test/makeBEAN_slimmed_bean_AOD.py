import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import sys
import os
import copy

####################################################################
## Global job options

REPORTEVERY = 100
WANTSUMMARY = False

####################################################################
## Define the process
process = cms.Process('BEANs')#"topDileptonNtuple")
#SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",ignoreTotal = cms.untracked.int32(1) )

op_inputScript = 'TopAnalysis.Configuration.Summer12.TTH_Inclusive_M_130_8TeV_pythia6_Summer12_DR53X_PU_S10_START53_V7A_v1_cff'#
op_json = ''#../json/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt'#
op_skipEvents = 0#
op_maxEvents = 10#
####################################################################
## Define input
    
if op_inputScript != '':
    #process.load(op_inputScript)
    inputFiles = cms.untracked.vstring('file:/afs/crc.nd.edu/user/c/cmuelle2/merge_v1/CMSSW_5_3_11/src/TopAnalysis/Configuration/analysis/common/ttH_MC.root')
    #inputFiles = cms.untracked.vstring('file:/afs/crc.nd.edu/user/c/cmuelle2/merge_v1/CMSSW_5_3_11/src/TopAnalysis/Configuration/analysis/common/SingleMu_DATA_v1.root')
    process.source = cms.Source("PoolSource",
            fileNames = inputFiles,
            secondaryFileNames = cms.untracked.vstring(),
            # the following is needed for new taus:
            dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
            inputCommands = cms.untracked.vstring(
                'keep *',
                'drop recoPFTaus_*_*_*'
            ))
else:
    print 'need an input script'
    exit(8889)
    
print "max events: ", op_maxEvents
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(op_maxEvents)
    )
    
if op_skipEvents > 0:
    process.source.skipEvents = cms.untracked.uint32(op_skipEvents)
        
        # Limit to json file (if passed as parameter)
if op_json != '':
    import FWCore.PythonUtilities.LumiList as LumiList
    import FWCore.ParameterSet.Types as CfgTypes
    myLumis = LumiList.LumiList(filename = op_json).getCMSSWString().split(',')
    process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
    process.source.lumisToProcess.extend(myLumis)


####################################################################
# === Parse external arguments === #
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing("analysis")
# 'jobParams' parameter form:
#
# <era>_<subera>_<type>_<sample number>
#
# <era>                 = 2011, 2012
# <subera> [N/A for MC] = A, B, C...
# <type>                = MC-sigFullSim, MC-sigFastSim, MC-bg, data-PR, data-RR, data-RRr
# <sample number>       = See https://twiki.cern.ch/twiki/bin/view/CMS/TTbarHiggsTauTau#Process_info
#
# Examples:
# 2011_X_MC-sig_2500
# 2011_B_data-PR_-11
# 2012_X_MC-bg_2400
# 2012_B_data-PR_muon
options.register ('jobParams',
                  #'multicrab',
                  #'2012_A_data-PR_-11',# -12012A collisions
                  #'2012_B_data-PR_-11',# -112012B collisions
                  #'2012_X_MC-sigFastSim_120',# 120signal_M-120
                  #'2012_X_MC-bg_2500',# 2500  TTbar
                  #'2012_X_MC-bg_2524',# 2524  TTbar + W
                  #'2012_X_MC-bg_2523',# 2523  TTbar + Z
                  #'2012_X_MC-bg_2400',# 2400  W+jets
                  #'2012_X_MC-bg_2800',# 2800  Z+jets (50<M)
                  #'2012_X_MC-bg_2850',# 2850  Z+jets (10<M<50)
                  #'2012_X_MC-bg_2700',# 2700  WW
                  #'2012_X_MC-bg_2701',# 2701  WZ
                  #'2012_X_MC-bg_2702',# 2702  ZZ
                  #'2012_X_MC-bg_2504',# 2504  sT+W
                  #'2012_X_MC-bg_2505',# 2505  sTbar+W
                  #'2012_X_MC-bg_2600',# 2600  sT-sCh
                  #'2012_X_MC-bg_2501',# 2501  sTbar-sCh
                  #'2012_X_MC-bg_2602',# 2602  sT-tCh
                  #'2012_X_MC-bg_2503',# 2503  sTbar-tCh
                  #'2012_X_MC-bg_9115',# 9115  TTH_115_Fast
                  #'2012_X_MC-bg_9120',# 9120  TTH_120_Fast
                  '2012_X_MC-bg_9125',# 9125  TTH_125_Fast
                  VarParsing.VarParsing.multiplicity.singleton,
                  VarParsing.VarParsing.varType.string )
options.parseArguments()

# === Parse Job Params === #
import shlex;
my_splitter = shlex.shlex(options.jobParams, posix=True);
my_splitter.whitespace = '_';
my_splitter.whitespace_split = True;
jobParams= list(my_splitter);

# === Job params error checking === #
if len(jobParams) != 4:
    print "ERROR: jobParams set to '" + options.jobParams + "' must have exactly 4 arguments (check config file for details). Terminating."; sys.exit(1);

if (jobParams[0] != "2011") and (jobParams[0] != "2012"):
    print "ERROR: era set to '" + jobParams[0] + "' but it must be '2011' or '2012'"; sys.exit(1);

runOnMC= ((jobParams[2]).find('MC') != -1);
runOnFastSim= ((jobParams[2]).find('MC-sigFastSim') != -1);
if (not runOnMC) and ((jobParams[1] != 'A') and (jobParams[1] != 'B') and (jobParams[1] != 'C') and (jobParams[1] != 'D')):
    print "ERROR: job set to run on collision data from sub-era '" + jobParams[1] + "' but it must be 'A', 'B', 'C', or 'D'."; sys.exit(1);
    
if (jobParams[2] != "data-PR") and (jobParams[2] != "data-RR") and (jobParams[2] != "data-RRr")and (jobParams[2] != "MC-bg") and (jobParams[2] != "MC-sigFullSim") and (jobParams[2] != "MC-sigFastSim"):
    print "ERROR: sample type set to '" + jobParams[2] + "' but it can only be 'data-PR', 'data-RR', 'data-RRr', 'MC-bg', 'MC-sigFullSim', or 'MC-sigFastSim'."; sys.exit(1);
    
sampleNumber= int(jobParams[3]);
if (runOnMC and sampleNumber < 0):
    print "ERROR: job set to run on MC but sample number set to '" + sampleNumber + "' when it must be positive."; sys.exit(1);
    
if (not runOnMC and sampleNumber >= 0):
    print "ERROR: job set to run on collision data but sample number set to '" + sampleNumber + "' when it must be negative."; sys.exit(1);


####################################################################
## Configure message logger

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = 'INFO'
process.MessageLogger.cerr.FwkReport.reportEvery = REPORTEVERY

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(WANTSUMMARY)
)

####################################################################
## Geometry and Detector Conditions

process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

if runOnMC:
    globalTag = 'START53_V7G::All'
else:
    globalTag = 'FT_53_V6C_AN4::All'
    if jobParams[2] == "data-PR":
        globalTag = 'GR_P_V42_AN4::All'
    elif jobParams[1]=='C' and jobParams[2] == "data-RR":
        globalTag = 'FT53_V10A_AN4::All'
        
process.GlobalTag.globaltag = cms.string( globalTag )
print "Using global tag: ", process.GlobalTag.globaltag

process.load("Configuration.StandardSequences.MagneticField_cff")



####################################################################
## HCAL Noise filter

process.load('CommonTools/RecoAlgos/HBHENoiseFilter_cfi')
process.HBHENoiseFilter.minIsolatedNoiseSumE = cms.double(999999.)
process.HBHENoiseFilter.minNumIsolatedNoiseChannels = cms.int32(999999)
process.HBHENoiseFilter.minIsolatedNoiseSumEt = cms.double(999999.)



####################################################################
## Beam scraping filter

process.scrapingFilter = cms.EDFilter("FilterOutScraping",
    applyfilter = cms.untracked.bool(True),
    debugOn     = cms.untracked.bool(False),
    numtrack    = cms.untracked.uint32(10),
    thresh      = cms.untracked.double(0.25)
    )



####################################################################
## ECAL laser correction filter

process.load("RecoMET.METFilters.ecalLaserCorrFilter_cfi")



####################################################################
## Primary vertex filtering

from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    "PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone( minNdof = cms.double(4.0), maxZ = cms.double(24.0) ),
    src=cms.InputTag('offlinePrimaryVertices')
    )



####################################################################
## Trigger filtering

# Get the central diLepton trigger lists, and set up filter
from TopAnalysis.TopFilter.sequences.diLeptonTriggers_cff import *
process.load("TopAnalysis.TopFilter.filters.TriggerFilter_cfi")
process.filterTrigger.TriggerResults = cms.InputTag('TriggerResults','','HLT')
process.filterTrigger.printTriggers = False
# if op_mode == 'mumu':
#     process.filterTrigger.hltPaths  = mumuTriggers
# elif op_mode == 'emu':
#     process.filterTrigger.hltPaths  = emuTriggers
# elif op_mode == 'ee':
#     process.filterTrigger.hltPaths  = eeTriggers
#else:
process.filterTrigger.hltPaths = eeTriggers + emuTriggers + mumuTriggers
    
#print "Printing triggers: ", process.filterTrigger.printTriggers



####################################################################
## Jet corrections

if runOnMC:
    jetCorr = ('AK5PFchs', ['L1FastJet','L2Relative','L3Absolute'])
else:
    jetCorr = ('AK5PFchs', ['L1FastJet','L2Relative','L3Absolute', 'L2L3Residual'])
    
## gen jet collections
if runOnMC:
    genjetTag_ = 'ak5GenJets'
else:
    genjetTag_ = 'none'

####################################################################
## PF2PAT sequence
process.load( "TopQuarkAnalysis.Configuration.patRefSel_outputModule_cff" )
process.out.fileName = cms.untracked.string("merged_bean.root")
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out.outputCommands +=patEventContent
process.out.SelectEvents.SelectEvents = []

process.load("PhysicsTools.PatAlgos.patSequences_cff")

#pfpostfix = "PFlow"
pfpostfix = ""

from PhysicsTools.PatAlgos.tools.pfTools import *

usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=runOnMC, postfix=pfpostfix, jetCorrections=jetCorr, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), typeIMetCorrections=True) 

from PhysicsTools.PatAlgos.selectionLayer1.electronSelector_cfi import *
from PhysicsTools.PatAlgos.selectionLayer1.muonSelector_cfi import *
from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *

# Produce pat trigger content
process.load("PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cff")

#turn off PF2PAT Top Projection....Charlie Projection!

applyPostfix( process, 'pfNoPileUp'  , pfpostfix ).enable = True
applyPostfix( process, 'pfNoMuon'    , pfpostfix ).enable = False
applyPostfix( process, 'pfNoElectron', pfpostfix ).enable = False
applyPostfix( process, 'pfNoJet'     , pfpostfix ).enable = False
applyPostfix( process, 'pfNoTau'     , pfpostfix ).enable = False

####################################################################
## Set up selections for PF2PAT & PAT objects: Electrons

# MVA ID
process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
process.eidMVASequence = cms.Sequence(process.mvaTrigV0
                                      +process.mvaNonTrigV0)
getattr(process,'patElectrons'+pfpostfix).electronIDSources.mvaTrigV0 = cms.InputTag("mvaTrigV0")
getattr(process,'patElectrons'+pfpostfix).electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0")
getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'patElectrons'+pfpostfix),
                                                process.eidMVASequence *
                                                getattr(process,'patElectrons'+pfpostfix)
                                                )

process.pfPileUp.checkClosestZVertex = cms.bool(False)

process.pfSelectedElectrons.cut = 'pt > 5.'# && gsfTrackRef.isNonnull && gsfTrackRef.trackerExpectedHitsInner.numberOfLostHits < 2'

# Switch isolation cone to 0.3 and set cut to 0.15
process.pfIsolatedElectrons.doDeltaBetaCorrection = True   # not really a 'deltaBeta' correction, but it serves
process.pfIsolatedElectrons.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFId")
process.pfIsolatedElectrons.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFId"))
process.pfIsolatedElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))
process.pfIsolatedElectrons.isolationCut = 99.0#0.2

process.pfElectronsFromVertex.d0Cut = 99.0
process.pfElectronsFromVertex.dzCut = 99.0

process.patElectrons.isolationValues = cms.PSet(
    pfChargedHadrons = cms.InputTag("elPFIsoValueCharged03PFId"),
    pfChargedAll = cms.InputTag("elPFIsoValueChargedAll03PFId"),
    pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU03PFId"),
    pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral03PFId"),
    pfPhotons = cms.InputTag("elPFIsoValueGamma03PFId") )


process.selectedPatElectrons.cut = ''#'electronID("mvaTrigV0") > 0.5 && passConversionVeto'
            #cant do this on python level :-(
            #' && abs(gsfTrack().dxy(vertex_.position())) < 0.04'

####################################################################
## Set up selections for PF2PAT & PAT objects: Muons

process.pfSelectedMuons.cut = 'pt > 5.'


# Switch isolation cone to 0.3 and set cut to 0.15
process.pfIsolatedMuons.doDeltaBetaCorrection = True
process.pfIsolatedMuons.deltaBetaIsolationValueMap = cms.InputTag("muPFIsoValuePU03", "", "")
process.pfIsolatedMuons.isolationValueMapsCharged = [cms.InputTag("muPFIsoValueCharged03")]
process.pfIsolatedMuons.isolationValueMapsNeutral = [cms.InputTag("muPFIsoValueNeutral03"), cms.InputTag("muPFIsoValueGamma03")]
process.pfIsolatedMuons.isolationCut = 99.0#0.2

process.pfMuonsFromVertex.d0Cut = 99.0
process.pfMuonsFromVertex.dzCut = 99.0

process.patMuons.isolationValues = cms.PSet(
        pfNeutralHadrons = cms.InputTag("muPFIsoValueNeutral03"),
        pfChargedAll = cms.InputTag("muPFIsoValueChargedAll03"),
        pfPUChargedHadrons = cms.InputTag("muPFIsoValuePU03"),
        pfPhotons = cms.InputTag("muPFIsoValueGamma03"),
        pfChargedHadrons = cms.InputTag("muPFIsoValueCharged03")
        )


process.selectedPatMuons.cut = ''#'isGlobalMuon && pt > 20 && abs(eta) < 2.5'



####################################################################
## Set up selections for PF2PAT & PAT objects: Jets

#process.selectedPatJets.cut = 'abs(eta)<5.4'

## taus
tauCut = 'pt > 5. && abs(eta) < 2.5 && tauID("decayModeFinding")'
process.selectedPatTaus.cut = tauCut


process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")


####################################################################
## Basic debugging analyzer

#process.load("TopAnalysis.TopAnalyzer.CheckDiLeptonAnalyzer_cfi")
#process.analyzeDiLepton.electrons = 'fullySelectedPatElectronsCiC'
#process.analyzeDiLepton.muons = 'fullySelectedPatMuons'

signal = True
viaTau = False
alsoViaTau = True
ttbarV = True

####################################################################
## Define which collections (including which corrections) to be used in nTuple

jetCollection = "hardJets"

####################################################################
## Build Jet Collections

if runOnMC:
	jet_gen_seq = cms.Sequence(process.genParticlesForJets)
else:
	jet_gen_seq = cms.Sequence()

process.load("RecoJets.JetProducers.SubjetsFilterjets_cfi")
process.CA12JetsCA3FilterjetsPF.src = getattr(process,'pfJets'+pfpostfix).src
getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'pfJets'+pfpostfix),getattr(process,'pfJets'+pfpostfix)*process.filtjet_pf_seq)

if runOnMC:
    process.load("RecoJets.Configuration.GenJetParticles_cff")
    from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
    process.ca12GenJets = ca4GenJets.clone( rParam = cms.double(1.2) )
    jet_gen_seq = jet_gen_seq * process.ca12GenJets * process.filtjet_gen_seq
    genFatJetsCollection = cms.InputTag('ca12GenJets')
    genSubJetsCollection = cms.InputTag('CA12JetsCA3FilterjetsGen','subjets')
    genFilterJetsCollection = cms.InputTag('CA12JetsCA3FilterjetsGen','filterjets')
else:
    genFatJetsCollection = None
    genSubJetsCollection = None
    genFilterJetsCollection = None

addJetCollection(
    process,
    cms.InputTag('CA12JetsCA3FilterjetsPF','fatjet'),
    algoLabel = 'CA12Fat',
    typeLabel = 'PF',
    doJTA  = True,
    doBTagging = True,
    doType1MET = False,
    jetCorrLabel = None,#('kt6', ['L2Relative','L3Absolute']),
    doJetID = False,
    genJetCollection = genFatJetsCollection
)

addJetCollection(
    process,
    cms.InputTag('CA12JetsCA3FilterjetsPF','subjets'),
    algoLabel = 'CA3Sub',
    typeLabel = 'PF',
    doJTA  = True,
    doBTagging = True,
    doType1MET = False,
    jetCorrLabel = None,#('kt6', ['L2Relative','L3Absolute']),
    doJetID = False,
    genJetCollection = genSubJetsCollection
)

addJetCollection(
    process,
    cms.InputTag('CA12JetsCA3FilterjetsPF','filterjets'),
    algoLabel = 'CA12FatCA3Filter',
    typeLabel = 'PF',
    doJTA  = True,
    doBTagging = True,
    doType1MET = False,
    jetCorrLabel = None,#('kt6', ['L2Relative','L3Absolute']),
    doJetID = False,
    genJetCollection = genFilterJetsCollection
)

# if runOnMC:
#     getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'patJets'+pfpostfix),
#                                                             getattr(process,'patJets'+pfpostfix)
#                                                             *process.jetTracksAssociatorAtVertexCA12FatCA3FilterPF
#                                                             *process.jetTracksAssociatorAtVertexCA3SubPF
#                                                             *process.jetTracksAssociatorAtVertexCA12FatPF
#                                                             *process.btaggingCA12FatCA3FilterPF
#                                                             *process.btaggingCA3SubPF
#                                                             *process.btaggingCA12FatPF
#                                                             *process.patJetChargeCA12FatCA3FilterPF
#                                                             *process.patJetChargeCA3SubPF
#                                                             *process.patJetChargeCA12FatPF
#                                                             *process.patJetGenJetMatchCA12FatCA3FilterPF
#                                                             *process.patJetGenJetMatchCA3SubPF
#                                                             *process.patJetGenJetMatchCA12FatPF
#                                                             *process.patJetPartonMatchCA12FatCA3FilterPF
#                                                             *process.patJetPartonMatchCA3SubPF
#                                                             *process.patJetPartonMatchCA12FatPF
#                                                             *process.patJetPartonAssociationCA12FatCA3FilterPF
#                                                             *process.patJetPartonAssociationCA3SubPF
#                                                             *process.patJetPartonAssociationCA12FatPF
#                                                             *process.patJetFlavourAssociationCA12FatCA3FilterPF
#                                                             *process.patJetFlavourAssociationCA3SubPF
#                                                             *process.patJetFlavourAssociationCA12FatPF
#                                                             *process.patJetsCA12FatCA3FilterPF
#                                                             *process.patJetsCA3SubPF
#                                                             *process.patJetsCA12FatPF
#                                                             *process.selectedPatJetsCA12FatCA3FilterPF
#                                                             *process.selectedPatJetsCA3SubPF
#                                                             *process.selectedPatJetsCA12FatPF
#                                                             )
# else:
#     getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'patJets'+pfpostfix),
#                                                             getattr(process,'patJets'+pfpostfix)
#                                                             *process.jetTracksAssociatorAtVertexCA12FatCA3FilterPF
#                                                             *process.jetTracksAssociatorAtVertexCA3SubPF
#                                                             *process.jetTracksAssociatorAtVertexCA12FatPF
#                                                             *process.btaggingCA12FatCA3FilterPF
#                                                             *process.btaggingCA3SubPF
#                                                             *process.btaggingCA12FatPF
#                                                             *process.patJetChargeCA12FatCA3FilterPF
#                                                             *process.patJetChargeCA3SubPF
#                                                             *process.patJetChargeCA12FatPF
#                                                             *process.patJetsCA12FatCA3FilterPF
#                                                             *process.patJetsCA3SubPF
#                                                             *process.patJetsCA12FatPF
#                                                             *process.selectedPatJetsCA12FatCA3FilterPF
#                                                             *process.selectedPatJetsCA3SubPF
#                                                             *process.selectedPatJetsCA12FatPF
#                                                             )

#process.load("RecoJets.JetProducers.HEPTopJetParameters_cfi")
#process.HEPTopJetsPF.src = getattr(process,'pfJets'+pfpostfix).src
#getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'pfJets'+pfpostfix),getattr(process,'pfJets'+pfpostfix)*process.heptopjet_pf_seq)
	
# if runOnMC:
#     process.load("RecoJets.Configuration.GenJetParticles_cff")
#     from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
#     process.ca15GenJets = ca4GenJets.clone( rParam = cms.double(1.5) )
#     jet_gen_seq = jet_gen_seq * process.ca15GenJets * process.heptopjet_gen_seq
#     genFatJetsCollection = cms.InputTag('ca15GenJets')
#     genSubJetsCollection = cms.InputTag('HEPTopJetsGen', 'subjets')
# else:
#     genFatJetsCollection = None
#     genSubJetsCollection = None    

# addJetCollection(
#     process, 
#     cms.InputTag('HEPTopJetsPF', 'fatjet'),
#     algoLabel = 'HEPTopFat',
#     typeLabel = 'PF',
#     doJTA=True,
#     doBTagging=True,
#     doType1MET=False,
#     jetCorrLabel = None,#('kt6', ['L2Relative','L3Absolute']),
#     genJetCollection = genFatJetsCollection,
#     doJetID = False
# )

    # Subjets
# addJetCollection(
#     process, 
#     cms.InputTag('HEPTopJetsPF', 'subjets'),
#     algoLabel = 'HEPTopSub',
#     typeLabel = 'PF',
#     doJTA=True,
#     doBTagging=True,
#     doType1MET=False,
#     jetCorrLabel = None,#('kt6', ['L2Relative','L3Absolute']),
#     genJetCollection = genSubJetsCollection,
#     doJetID = False
# )

# if runOnMC:	
#     getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'patJets'+pfpostfix),
#                                                             getattr(process,'patJets'+pfpostfix)
#                                                             *process.jetTracksAssociatorAtVertexHEPTopSubPF
#                                                             *process.jetTracksAssociatorAtVertexHEPTopFatPF
#                                                             *process.btaggingHEPTopSubPF
#                                                             *process.btaggingHEPTopFatPF
#                                                             *process.patJetChargeHEPTopSubPF
#                                                             *process.patJetChargeHEPTopFatPF
#                                                             *process.patJetGenJetMatchHEPTopSubPF
#                                                             *process.patJetGenJetMatchHEPTopFatPF
#                                                             *process.patJetPartonMatchHEPTopSubPF
#                                                             *process.patJetPartonMatchHEPTopFatPF
#                                                             *process.patJetPartonAssociationHEPTopSubPF
#                                                             *process.patJetPartonAssociationHEPTopFatPF
#                                                             *process.patJetFlavourAssociationHEPTopSubPF
#                                                             *process.patJetFlavourAssociationHEPTopFatPF
#                                                             *process.patJetsHEPTopSubPF
#                                                             *process.patJetsHEPTopFatPF
#                                                             *process.selectedPatJetsHEPTopSubPF
#                                                             *process.selectedPatJetsHEPTopFatPF
#                                                             )
# else:
#     getattr(process, 'patPF2PATSequence'+pfpostfix).replace(getattr(process,'patJets'+pfpostfix),
#                                                             getattr(process,'patJets'+pfpostfix)
#                                                             *process.jetTracksAssociatorAtVertexHEPTopSubPF
#                                                             *process.jetTracksAssociatorAtVertexHEPTopFatPF
#                                                             *process.btaggingHEPTopSubPF
#                                                             *process.btaggingHEPTopFatPF
#                                                             *process.patJetChargeHEPTopSubPF
#                                                             *process.patJetChargeHEPTopFatPF
#                                                             *process.patJetsHEPTopSubPF
#                                                             *process.patJetsHEPTopFatPF
#                                                             *process.selectedPatJetsHEPTopSubPF
#                                                             *process.selectedPatJetsHEPTopFatPF
#                                                             )

process.load("TopAnalysis.TopUtils.JetEnergyScale_cfi")

process.load("TopAnalysis.TopFilter.filters.JetIdFunctorFilter_cfi")
process.goodIdJets.jets    = cms.InputTag("scaledJetEnergy:selectedPatJets")
process.goodIdJets.jetType = cms.string('PF')
process.goodIdJets.version = cms.string('FIRSTDATA')
process.goodIdJets.quality = cms.string('LOOSE')

process.hardJets = selectedPatJets.clone(src = 'goodIdJets', cut = 'pt > 5 & abs(eta) < 2.4') 

# Additional properties for jets like jet charges
process.load("TopAnalysis.HiggsUtils.producers.JetPropertiesProducer_cfi")
process.jetProperties.src = jetCollection

#add super taggers
switchJetCollection(process,
                    cms.InputTag('pfJets'+pfpostfix),
                    doJTA              = True,
                    doBTagging         = True,
                    btagInfo           = cms.vstring('impactParameterTagInfos','secondaryVertexTagInfos','softPFMuonsTagInfos','softPFElectronsTagInfos'),
                    btagdiscriminators = cms.vstring('jetBProbabilityBJetTags','jetProbabilityBJetTags','trackCountingHighPurBJetTags','trackCountingHighEffBJetTags','simpleSecondaryVertexHighEffBJetTags','simpleSecondaryVertexHighPurBJetTags','combinedSecondaryVertexBJetTags','combinedSecondaryVertexV1BJetTags','combinedSecondaryVertexSoftPFLeptonV1BJetTags'),
                    jetCorrLabel       = jetCorr,
                    doType1MET         = False,
                    genJetCollection   = cms.InputTag('ak5GenJets'),
                    doJetID            = True,
                    postfix            = pfpostfix
                    )



process.load('CondCore.DBCommon.CondDBSetup_cfi')
process.BTauMVAJetTagComputerRecord = cms.ESSource('PoolDBESSource',
                                                   process.CondDBSetup,
                                                   timetype = cms.string('runnumber'),
                                                   toGet = cms.VPSet(cms.PSet(
    record = cms.string('BTauGenericMVAJetTagComputerRcd'),
    tag = cms.string('MVAComputerContainer_Retrained53X_JetTags_v2')
    )),
                                                   connect = cms.string('frontier://FrontierProd/CMS_COND_PAT_000'),
                                                   BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService'))

process.es_prefer_BTauMVAJetTagComputerRecord = cms.ESPrefer('PoolDBESSource','BTauMVAJetTagComputerRecord')

####################################################################
## removal of unnecessary modules
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'patPFParticles'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'patCandidateSummary'+pfpostfix))

getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'selectedPatPFParticles'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'selectedPatCandidateSummary'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'countPatElectrons'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'countPatMuons'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'countPatLeptons'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'countPatJets'+pfpostfix))
getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'countPatPFParticles'+pfpostfix))

getattr(process,'patPF2PATSequence'+pfpostfix).remove(getattr(process,'pfPhotonSequence'+pfpostfix))

massSearchReplaceAnyInputTag(getattr(process,'patPF2PATSequence'+pfpostfix),'pfNoTau'+pfpostfix,'pfJets'+pfpostfix)
##############LETS MAKE SOME BEEEEAAAANNNSSSSSS#####################

process.load("CMGTools.External.pujetidsequence_cff")

from RecoMuon.MuonIsolationProducers.caloExtractorByAssociatorBlocks_cff import *
from RecoMuon.MuonIsolationProducers.trackExtractorBlocks_cff import *
process.load('Configuration.StandardSequences.MagneticField_38T_cff')

process.BNproducer = cms.EDProducer('BEANmaker',
                                    pfmetTag = cms.InputTag("patMETs"),#patMETs"),
#                                    pfmetTag_type1correctedRECO = cms.InputTag("pfType1CorrectedMet"),
#                                    pfmetTag_uncorrectedPF2PAT  = cms.InputTag("patPFMet"),
#                                    pfmetTag_uncorrectedRECO    = cms.InputTag("pfMET"),
                                    eleTag = cms.InputTag("selectedPatElectrons"),#selectedPatElectrons"),
                                    genParticleTag = cms.InputTag("genParticles"),
                                    pfjetTag = cms.InputTag("selectedPatJets"),
                                    genjetTag = cms.InputTag(genjetTag_),
#                                     pfsfpatfatjetsTag = cms.InputTag('selectedPatJetsCA12FatPF'),
#                                     pfsfpatsubjetsTag = cms.InputTag('selectedPatJetsCA3SubPF'),
#                                     pfsfpatfilterjetsTag = cms.InputTag('selectedPatJetsCA12FatCA3FilterPF'),
#                                     pfsfrecofatjetsTag = cms.InputTag('CA12JetsCA3FilterjetsPF','fatjet'),
#                                     pfsfsubjettiness1Tag = cms.InputTag('CA12JetsCA3FilterjetsPF','tau1'),
#                                     pfsfsubjettiness2Tag = cms.InputTag('CA12JetsCA3FilterjetsPF','tau2'),
#                                     pfsfsubjettiness3Tag = cms.InputTag('CA12JetsCA3FilterjetsPF','tau3'),
#                                     pfsfsubjettiness4Tag = cms.InputTag('CA12JetsCA3FilterjetsPF','tau4'),
#                                     pfttpatfatjetsTag = cms.InputTag('selectedPatJetsHEPTopFatPF'),
#                                     pfttpatsubjetsTag = cms.InputTag('selectedPatJetsHEPTopSubPF'),
#                                     pftttoptagsTag = cms.InputTag('HEPTopJetsPF','toptag'),
#                                     pfttrecofatjetsTag = cms.InputTag('HEPTopJetsPF','fatjet'),
#                                     pfttsubjettiness1Tag = cms.InputTag('HEPTopJetsPF','tau1'),
#                                     pfttsubjettiness2Tag = cms.InputTag('HEPTopJetsPF','tau2'),
#                                     pfttsubjettiness3Tag = cms.InputTag('HEPTopJetsPF','tau3'),
#                                     pfttsubjettiness4Tag = cms.InputTag('HEPTopJetsPF','tau4'),
                                    muonTag = cms.InputTag("selectedPatMuons"),
                                    photonTag = cms.InputTag("none"),
                                    #EBsuperclusterTag = cms.InputTag("correctedHybridSuperClusters"),
                                    #EEsuperclusterTag = cms.InputTag("correctedMulti5x5SuperClustersWithPreshower"),

                                    #reducedBarrelRecHitCollection = cms.InputTag("reducedEcalRecHitsEB"),
                                    #reducedEndcapRecHitCollection = cms.InputTag("reducedEcalRecHitsEE"),

                                    #trackTag = cms.InputTag("generalTracks"),
                                    tauTag = cms.InputTag("selectedPatTaus"),
                                    triggerResultsTag = cms.InputTag("TriggerResults::HLT"),
                                    #gtSource = cms.InputTag("gtDigis"),
                                    pvTag = cms.InputTag("offlinePrimaryVertices"),
                                    #triggerSummaryTag = cms.InputTag("hltTriggerSummaryAOD"),
                                    #dcsTag = cms.InputTag("scalersRawToDigi"),
                                    hltProcessName = cms.string("HLT"),
                                    eventWeight = cms.double(0.0126976903794279),
                                    minSCEt = cms.double(10),
                                    minPhotonEt = cms.double(10),
                                    minJetPt = cms.double(10),
                                    minTrackPt = cms.double(10),
                                    verbose = cms.bool(False),
                                    fillTrackHitInfo = cms.bool(False),
                                    fillTrackIsoInfo = cms.bool(False),
                                    CaloExtractorPSet  = cms.PSet(MIsoCaloExtractorByAssociatorTowersBlock),
                                    TrackExtractorPSet = cms.PSet(MIsoTrackExtractorBlock),
                                    sample = cms.int32(sampleNumber),
                                    maxAbsZ = cms.untracked.double(24)
                                    )

process.q2weights = cms.EDProducer('Q2Weights')

####################################################################
## Paths, one with preselection, one without for signal samples

process.metseq = cms.Sequence(
    process.pfJetMETcorr *
    process.pfType1CorrectedMet
    )

process.content = cms.EDAnalyzer("EventContentAnalyzer")

if signal or higgsSignal or zGenInfo:
    process.pNtuple = cms.Path(
        process.goodOfflinePrimaryVertices *
        process.q2weights *
        #jet_gen_seq *
        getattr(process,'patPF2PATSequence'+pfpostfix) *
        process.metseq *
        process.pfTausBase *
        process.PFTau *
        process.BNproducer
        )


process.out.outputCommands.extend( [
    'drop *',
    'keep *_BNproducer_*_*'
    ])

####################################################################
## Signal catcher for more information on errors

process.load("TopAnalysis.TopUtils.SignalCatcher_cfi")

#Dump python config if wished
outfile = open('dumpedConfig.py','w'); print >> outfile,process.dumpPython(); outfile.close()
