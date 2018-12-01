from .check_fastqs import CheckFastqs
from .trim_adapters import TrimAdapters, TrimAdaptersCohort
from .align_to_reference_and_add_read_group import (
    AlignToReferenceAndAddReadGroup,
    AlignToReferenceAndAddReadGroupCohort
)
from .fix_read_groups import FixReadGroups
from .validate_sam import ValidateSam
from .sort_and_compress_alignment import (
    SortAndCompressAlignment,
    SortAndCompressAlignmentCohort
)
from .delete_sam_files import DeleteSamFiles, DeleteSamFilesCohort
from .mark_duplicates import MarkDuplicates, MarkDuplicatesCohort
from .index_alignment import IndexAlignment, IndexAlignmentCohort

# DEPRECATED part of the pipeline:
#
#  from .create_realignment_intervals import CreateRealignmentIntervals
#  from .realign_around_indels import RealignAroundIndels
#  from .create_recalibration_table import CreateRecalibrationTable
#  from .recalibrate_alignment_scores import RecalibrateAlignmentScores

from .make_gvcf import MakeGVCF, MakeGVCFCohort
from .call_targets import CallTargets
from .reset_filters import ResetFilters, ResetFiltersCohort
from .joint_genotyping import JointGenotyping
from .merge_vcfs import MergeVCFs
from .annotate_with_snpsift_dbsnp import AnnotateWithSnpsiftDbSNP
from .select_snps import SelectSNPs
from .select_indels import SelectIndels
from .filter_snps import FilterSNPs
from .filter_indels import FilterIndels
from .combine_variants import CombineVariants
from .filter_genotypes import FilterGenotypes
from .extract_sample import ExtractSample
from .keep_reportable_genotypes import KeepReportableGenotypes
