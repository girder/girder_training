import itk
import os

InputPixelType = itk.F
OutputPixelType = itk.UC
Dimensions = 2

numberOfIterations = 50
timeStep = 0.1
conductance = 0.4

outputFileName = os.path.splitext(inputFileName)[0] + '_out.png'
inputFileName = str(inputFileName)
outputFileName = str(outputFileName)

outputPixelTypeMin = itk.NumericTraits[OutputPixelType].min()
outputPixelTypeMax = itk.NumericTraits[OutputPixelType].max()

InputImageType = itk.Image[InputPixelType, Dimensions]
OutputImageType = itk.Image[OutputPixelType, Dimensions]
ReaderType = itk.ImageFileReader[InputImageType]
FilterType = itk.CurvatureAnisotropicDiffusionImageFilter[InputImageType, InputImageType]
RescalerType = itk.RescaleIntensityImageFilter[InputImageType, OutputImageType]
WriterType = itk.ImageFileWriter[OutputImageType]

reader = ReaderType.New()
reader.SetFileName(inputFileName)

cadFilter = FilterType.New()
cadFilter.SetInput(reader.GetOutput())
cadFilter.SetNumberOfIterations(numberOfIterations)
cadFilter.SetTimeStep(timeStep)
cadFilter.SetConductanceParameter(conductance)

rescalar = RescalerType.New()
rescalar.SetInput(cadFilter.GetOutput())
rescalar.SetOutputMinimum(outputPixelTypeMin)
rescalar.SetOutputMaximum(outputPixelTypeMax)

writer = WriterType.New()
writer.SetFileName(outputFileName)
writer.SetInput(rescalar.GetOutput())
writer.Update()
