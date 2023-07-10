import { Module } from '@nestjs/common';
import { DataController } from './data.controller';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataResolver } from './data.resolver';
import { IsDataExistedByHashValueConstraint } from './data.validator';

@Module({
	controllers: [DataController],
	providers: [DataService, DataResolver, IsDataExistedByHashValueConstraint],
	imports: [TypeOrmModule.forFeature([Data])],
})
export class DataModule {}
